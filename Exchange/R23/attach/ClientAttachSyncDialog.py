# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Exchange.R23.attach.AttachExchange import CR23AttachExchange
from Exchange.R23.attach.Utils import CAttachedClientInfoSyncStatus, CAttachedInfoTable, CDeAttachReason, insertAttachLogValues, setClientAttachesSynced
from Ui_ClientAttachSyncDialog import Ui_ClientAttachSyncDialog
from library.DialogBase import CDialogBase
from library.Utils import CChunkProcessor, forceBool, forceInt, forceRef, forceString


class CClientAttachSyncDialog(CDialogBase, Ui_ClientAttachSyncDialog):
    InsertChunkSize = 1000

    def __init__(self, parent, idList):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

        db = QtGui.qApp.db

        self._syncDatetime = None
        self._deathAttachTypeId = forceRef(db.translate('rbAttachType', 'code', '8', 'id'))

        self._attachedIdList = []
        self._deattachedIdList = []
        if idList:
            tableACI = db.table('AttachedClientInfo')
            cols = [
                tableACI['id'],
                db.makeField(tableACI['endDate'].isNull()).alias('toAttach')
            ]
            for rec in db.iterRecordList(tableACI, cols, tableACI['id'].inlist(idList)):
                id = forceRef(rec.value('id'))
                if forceBool(rec.value('toAttach')):
                    self._attachedIdList.append(id)
                else:
                    self._deattachedIdList.append(id)

        self.edtSelectedA.setText(str(len(self._attachedIdList)))
        self.edtSelectedD.setText(str(len(self._deattachedIdList)))

        self.resetProgressBar()

        self.setWindowTitle(u'Синхронизация с ТФОМС')

    def resetProgressBar(self, minimum=0, maximum=1, value=0, text=u'', fmt=u''):
        self.progressBar.setRange(minimum, maximum)
        self.progressBar.setValue(value)
        self.progressBar.setText(text)
        if fmt:
            self.progressBar.setFormat(fmt)

    @QtCore.pyqtSlot()
    def on_btnSync_clicked(self):
        widgetsToDisable = (
            self.chkCreateClientAttach,
            self.chkCreateClients,
            self.chkDeattachOnlyOnDeath,
            self.btnSync
        )
        for widget in widgetsToDisable:
            widget.setEnabled(False)

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.resetProgressBar(text=u'Синхронизация с ТФОМС ...')

            self._syncDatetime = QtCore.QDateTime.currentDateTime()
            if self._deattachedIdList:
                self.processDeattached()
            if self._attachedIdList:
                self.processAttached()

        except Exception as e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.warning(self, u'Внимание!', forceString(e))

        finally:
            QtGui.qApp.restoreOverrideCursor()
            self.resetProgressBar(value=1, text=u'Синхронизация завершена')

        for widget in widgetsToDisable:
            widget.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    @staticmethod
    def processAttachedQueryRecordList(idList, toDeAttach=False):
        db = QtGui.qApp.db
        tableACI = db.table('AttachedClientInfo')
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')

        table = tableACI.leftJoin(tableClient, tableClient['id'].eq(tableACI['client_id']))
        table = table.leftJoin(tableClientAttach, tableClientAttach['id'].eq(tableACI['attach_id']))
        cols = [
            tableACI['id'].alias('id'),
            tableClient['id'].alias('clientId'),
            tableClientAttach['id'].alias('attachId')
        ]
        if toDeAttach:
            cols.extend([
                tableACI['deattachReason'].alias('deattachReason'),
                db.makeField(tableClientAttach['endDate'].isNull()).alias('isClosed'),
                db.makeField(tableClientAttach['endDate'].dateEq(tableACI['endDate'])).alias('isSameDate')
            ])
        cond = [
            tableACI['id'].inlist(idList)
        ]
        return db.iterRecordList(table, cols, cond)

    def processAttached(self):
        u"""
        Обрабатываем выбранные записи (для прикрепления) в AttachedClientInfo:
            1) ищем пациента и прикрепление в БД
            2) проставляем статус синхронизации AttachedClientInfo.syncStatus
            3) для найденных пациентов логгируем статус синхронизации AttachedClientInfo.syncStatus -> AttachLog.status
            4) для найденных прикреплений обновляем статус ClientAttach.sentToTFOMS = Synced
            5) если прикрепление не найдено и выставлен чекбокс "Добавлять прикрепления":
                закрываем предыдущие (несихронизированные) прикрепления пациента,
                добавляем прикрепление из ТФОМС
        """
        isCreateAttach = self.chkCreateClientAttach.isChecked()
        isCreateClients = self.chkCreateClients.isChecked()

        count = 0
        countCreated = 0
        countClientsCreated = 0
        countSynced = 0
        countNoAttach = 0
        countNotFound = 0
        countTotal = len(self._attachedIdList)

        ChunkSize = CClientAttachSyncDialog.InsertChunkSize
        setSynced = CChunkProcessor(setClientAttachesSynced, ChunkSize)  # Обновляем ClientAttach.sentToTFOMS
        insertAttachLog = CChunkProcessor(insertAttachLogValues, ChunkSize, self._syncDatetime)  # Логгируем статусы синхронизации (logger.AttachLog)
        updateStatus = CChunkProcessor(CAttachedInfoTable.updateField, ChunkSize, 'syncStatus')  # Обновляем AttachedClientInfo.syncStatus
        createAndCloseOld = CChunkProcessor(CAttachedInfoTable.attachByTFOMS, ChunkSize)  # Добавляем полученные прикрепления, закрываем предыдущие
        closePrevious = CChunkProcessor(CAttachedInfoTable.closeAttaches, ChunkSize, False)  # Закрываем предыдущие прикрепления (для синхронизированных)
        createClients = CChunkProcessor(CR23AttachExchange.createClients, ChunkSize)  # Создаем пациентов в БД (для ненайденных)

        self.resetProgressBar(maximum=max(1, countTotal), fmt=u'Прикреплённые: %v/%m')
        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

        for i in xrange(0, countTotal, ChunkSize):
            idList = self._attachedIdList[i: i + ChunkSize]  # AttachedClientInfo.id
            CR23AttachExchange.findAttachedClientInfo(idList=idList)  # могли измениться перс. данные, прикрепления, ищем заново
            for rec in self.processAttachedQueryRecordList(idList):
                count += 1
                self.progressBar.setValue(count)
                if count % ChunkSize == 0:
                    QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

                id = forceRef(rec.value('id'))
                clientId = forceRef(rec.value('clientId'))
                attachId = forceRef(rec.value('attachId'))

                if clientId:
                    if attachId:
                        closePrevious(id)
                        setSynced(attachId)
                        status = CAttachedClientInfoSyncStatus.Attach_Synced
                        countSynced += 1
                    else:
                        if isCreateAttach:
                            createAndCloseOld(id)
                            status = CAttachedClientInfoSyncStatus.Attach_Created
                            countCreated += 1
                        else:
                            status = CAttachedClientInfoSyncStatus.Attach_NotMatch
                            countNoAttach += 1

                    insertAttachLog(clientId, status)
                    updateStatus(id, status)
                else:
                    if isCreateClients:
                        status = CAttachedClientInfoSyncStatus.Attach_Created
                        countClientsCreated += 1
                        createClients(id)
                        updateStatus(id, status)
                    else:
                        # ACI.syncStatus проставлен на этапе поиска
                        countNotFound += 1

            self.edtSyncedA.setText(str(countSynced))
            self.edtAttachedA.setText(str(countCreated))
            self.edtNoAttachA.setText(str(countNoAttach))
            self.edtNotFoundA.setText(str(countNotFound))
            self.edtClientsCreatedA.setText(str(countClientsCreated))

        setSynced.process()
        insertAttachLog.process()
        updateStatus.process()
        createAndCloseOld.process()
        closePrevious.process()
        createClients.process()

        self.resetProgressBar(value=1, text=u'Прикрепленные: завершено')

        self.edtSyncedA.setText(str(countSynced))
        self.edtAttachedA.setText(str(countCreated))
        self.edtNoAttachA.setText(str(countNoAttach))
        self.edtNotFoundA.setText(str(countNotFound))
        self.edtClientsCreatedA.setText(str(countClientsCreated))

        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def processDeattached(self):
        deattachOnlyOnDeath = self.chkDeattachOnlyOnDeath.isChecked()

        count = 0
        countTotal = len(self._deattachedIdList)
        countSynced = 0
        countDeattached = 0
        countAlreadyDeattached = 0
        countNotDeattached = 0
        countNotFound = 0
        countNoAttach = 0
        ChunkSize = CClientAttachSyncDialog.InsertChunkSize

        setSynced = CChunkProcessor(setClientAttachesSynced, ChunkSize)
        insertAttachLog = CChunkProcessor(insertAttachLogValues, ChunkSize, self._syncDatetime)
        deattachByTFOMS = CChunkProcessor(CAttachedInfoTable.deattachByTFOMS, ChunkSize)
        updateStatus = CChunkProcessor(CAttachedInfoTable.updateField, ChunkSize, 'syncStatus')
        deattachOnDeath = CChunkProcessor(CAttachedInfoTable.deattachOnDeath, ChunkSize, self._deathAttachTypeId)

        self.resetProgressBar(maximum=max(1, countTotal), fmt=u'Откреплённые: %v/%m')

        for i in xrange(0, countTotal, ChunkSize):
            idList = self._deattachedIdList[i: i + ChunkSize]  # AttachedClientInfo.id
            CR23AttachExchange.findAttachedClientInfo(idList=idList)  # могли измениться перс. данные, прикрепления, ищем заново
            for rec in self.processAttachedQueryRecordList(idList, True):
                count += 1
                self.progressBar.setValue(count)
                if count % ChunkSize == 0:
                    QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

                id = forceRef(rec.value('id'))
                clientId = forceRef(rec.value('clientId'))
                attachId = forceRef(rec.value('attachId'))
                isClosed = forceBool(rec.value('isClosed'))
                isSameDate = forceBool(rec.value('isSameDate'))
                deattachReason = forceInt(rec.value('deattachReason'))

                if clientId:
                    if attachId:
                        if isClosed:
                            if isSameDate:
                                status = CAttachedClientInfoSyncStatus.Deattach_Synced
                                countSynced += 1
                            else:
                                status = CAttachedClientInfoSyncStatus.Deattach_AlreadyDeattached
                                countAlreadyDeattached += 1
                            setSynced(attachId)
                        else:
                            if not deattachOnlyOnDeath or deattachReason == CDeAttachReason.ClientDeath:
                                deattachByTFOMS(id)
                                status = CAttachedClientInfoSyncStatus.Attach_Deattached
                                countDeattached += 1
                            else:
                                status = CAttachedClientInfoSyncStatus.Deattach_NotDeattached
                                countNotDeattached += 1
                    else:
                        if deattachReason == CDeAttachReason.ClientDeath:
                            deattachOnDeath(id)
                            status = CAttachedClientInfoSyncStatus.Attach_Deattached
                            countDeattached += 1
                        else:
                            status = CAttachedClientInfoSyncStatus.Deattach_NoAttach
                            countNoAttach += 1

                    insertAttachLog(clientId, status)
                    updateStatus(id, status)
                else:
                    # ACI.syncStatus проставлен на этапе поиска
                    countNotFound += 1

            self.edtSyncedD.setText(str(countSynced))
            self.edtDeattachedD.setText(str(countDeattached))
            self.edtAlreadyDeattachedD.setText(str(countAlreadyDeattached))
            self.edtNotDeattachedD.setText(str(countNotDeattached))
            self.edtNoAttachD.setText(str(countNoAttach))
            self.edtNotFoundD.setText(str(countNotFound))

        setSynced.process()
        insertAttachLog.process()
        deattachByTFOMS.process()
        updateStatus.process()
        deattachOnDeath.process()

        self.resetProgressBar(value=1, text=u'Откреплённые: завершено')

        self.edtSyncedD.setText(str(countSynced))
        self.edtDeattachedD.setText(str(countDeattached))
        self.edtAlreadyDeattachedD.setText(str(countAlreadyDeattached))
        self.edtNotDeattachedD.setText(str(countNotDeattached))
        self.edtNoAttachD.setText(str(countNoAttach))
        self.edtNotFoundD.setText(str(countNotFound))

        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
