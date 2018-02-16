# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################



#TODO: atronah: запуск голосового оповещения
#TODO: atronah: написать полноценный редактор очередей.



# ----- ЗАДАНИЯ ОТ п25
#+++TODO: atronah: ожидающие вызова должны выводиться одной волной, а не в отдельных очередях.
#+++TODO: atronah: Поддеражка вывода номерка через шаблон печати (eQueueTicket)
#+++TODO: atronah: привязка кнопок к кабинетам. Одна очередь на 3 кабинета.
#+++TODO: atronah: бронь/окно номерка и работы (например, раз в пол часа) для экстренных внеочередных
#+++TODO: atronah: отдельный девайс под вывод на экран.
#+++TODO: atronah: запрет одного типа работы на пациента в указанный период (чтобы повторно не делал один и тот же анализ)
#???TODO: atronah: Проверить, что при удалении события освобождается номерок
# -----

#-- ПРОВЕРКИ
#TODO: atronah: проверить, что будет, если сменить в процессе работы подразделение локальной кнопки через настройки (нужен ли перезапуск контроллера?)
#TODO: atronah: проверить вызов в разные каб через интерфейс
#TODO: atronah: убрать все debug-строки.

#-- CПОРНО:
#TODO: atronah: Изменение состояние номерка, при изменении статуса Job_Ticket.status (опционально)

#-- ОПТИМИЗАЦИЯ
#TODO: atronah: отправку уведомлений на отображение (адрес из таблицы EQHost, с типом "viewer")
#TODO: atronah: продумать варианты, при которых приложение может крашится и реализовать механизм автовосстановления работы (тихие краши)
#TODO: atronah: Решить проблему с тем, что одновременный вызов неск пациентов возможен только при наличии нескольких EQController
# (так как у каждого своя модель талонов).. А вот при одном контроллере - вызов след. всегда гасит текущего.
#TODO: atronah: проверки вида status in [Ready, Emergency] заменить на вызов какой-то статич функции.


#-- РЕШЕНО
#+++TODO: atronah: иконка для талонов со статусом "выдан"
#+++TODO: atronah: Загрузка/сохранение кнопок на основании связки EQHost.orgStructure_id -> OrgStructure_Job.master_id\eQueueType_id -> rbEQueueType
#+++TODO: atronah: Пометить талон готовым либо при записи на него пациента либо по вызову контекстного меню в выполнении работ (опция rbEQueueType.isImmediatelyReady)
#+++TODO: atronah: Отображение в списке "Выполнения работ" статуса номерка (не работы!)

from library.database import CDatabase

__author__ = 'atronah'

'''
    author: atronah
    date:   08.10.2014
    reason: To recieve and process eq events (next, prev patient).
'''


from PyQt4 import QtCore
from PyQt4 import QtSql
from library.ElectronicQueue.EQControl import CEQRemoteControl, CAbstractEQControl
from library.ElectronicQueue.EQControlModel import CEQControlModel
from library.ElectronicQueue.EQTicketModel import CEQTicketControlModel, EQTicketStatus
from library.ElectronicQueue.EQSettingsWindow import CEQSettingsWindow
from library.Utils import generalConnectionName




#TODO: atronah: deleteLater
class CEQController(QtCore.QObject):
    _instance = None
    _isAutoStart = False

    workStateChanged = QtCore.pyqtSignal(bool)
    workStarted = QtCore.pyqtSignal()
    workFinished = QtCore.pyqtSignal()

    ticketStatusChanged = QtCore.pyqtSignal(int) # (ticketId)

    PrevCallType = 0
    ReCallType = 1
    NextCallType = 2
    CustomCallType = 3


    class EQHost:
        Control = 0
        Controller = 1
        Transcoder = 2

    def __init__(self, dbConnectionName = None, parent = None):
        super(CEQController, self).__init__(parent)

        self._db = None
        self._ticketModelByQueueTypeId = {} #TODO: atronah: обновлять содержимое при изменении настроек кнопок.

        self.updateDatabase(dbConnectionName)



        self._updateModelsTimerId = None
        self._updateTimeout = 5.0

        self._queueTypeNameResolver = {}
        self._orgStructureNameResolver = {}
        self.initNameResolvers()

        self._controlModel = CEQControlModel(self)
        self._controlModel.setQueueNameResolver(self._queueTypeNameResolver)
        self._controlModel.setOrgStructureNameResolver(self._orgStructureNameResolver)
        self._controlModel.addedQueueType.connect(self.addQueueType)
        # self._controlModel.removedQueueType.connect(self.removeQueueType)
        self._controlModel.controlChanged.connect(self.updateButtonsState)
        self._controlModel.openedSettings.connect(self.openSettings)
        self._controlModel.controlActivated.connect(self.onControlActivated)

        self._controlModel.calledNext.connect(self.next)
        self._controlModel.calledPrev.connect(self.prev)
        self._controlModel.calledCustom.connect(self.custom)
        self._controlModel.reCalled.connect(self.reCall)

        self.workStarted.connect(self._controlModel.enableControls)
        self.workFinished.connect(self._controlModel.disableControls)

        self._settingsWindow = None

        self._currentTicketIdForControl = {}

        self.startWork()


    def updateDatabase(self, dbConnectionName = None):
        if not dbConnectionName:
            dbConnectionName = generalConnectionName()

        for queueTypeId in self._ticketModelByQueueTypeId.keys():
            self.removeQueueType(queueTypeId)
        self._db = QtSql.QSqlDatabase.database(dbConnectionName)



    @QtCore.pyqtSlot()
    def loadControls(self):
        query = QtSql.QSqlQuery(self._db)
        if query.exec_(u''' SELECT  EQHost.name,
                                    EQHost.address,
                                    EQHost.port,
                                    EQHost.orgStructure_id AS orgStructureId,
                                    EQHost.eQueueType_id AS eQueueTypeId
                            FROM EQHost
                            WHERE type = %s ''' % CEQController.EQHost.Control):
            self._controlModel.clear()
            while query.next():
                record = query.record()
                name = record.value('name').toString()
                host = record.value('address').toString()
                port = record.value('port').toInt()[0]
                orgStructureId = record.value('orgStructureId').toInt()[0]
                queueTypeId = record.value('eQueueTypeId').toInt()[0]
                if queueTypeId:
                    self._controlModel.addControl(orgStructureId, queueTypeId, CEQRemoteControl(host, port), name)
        else:
            CDatabase.checkDatabaseError(query.lastError(), query.lastQuery())


    @QtCore.pyqtSlot()
    def saveControls(self):
        valuesList = []
        deleteCondPartList = []
        for control in self._controlModel.controls():
            if not isinstance(control, CEQRemoteControl):
                continue
            values = {'name' : self._controlModel.name(control.controlId()),
                      'type' : CEQController.EQHost.Control,
                      'address' : control.host(),
                      'port' :  control.port(),
                      'orgStructure_id' : self._controlModel.orgStructureId(control.controlId()),
                      'eQueueType_id' : self._controlModel.queueTypeId(control.controlId())}
            valuesList.append(values)
            deleteCondPart = "('%(address)s', %(port)s)"
            deleteCondPartList.append(deleteCondPart % values)



        if valuesList:
            query = QtSql.QSqlQuery(self._db)

            insertStmtTemplate = """ INSERT INTO EQHost (`name`, `type`, `address`, `port`, `orgStructure_id`, `eQueueType_id`)
                                     VALUES  %s
                                     ON DUPLICATE KEY UPDATE
                                            `name` = VALUES(`name`),
                                            `orgStructure_id` = VALUES(`orgStructure_id`),
                                            `eQueueType_id` = VALUES(`eQueueType_id`)
                                        ;
                                 """
            valuesStatementTemplate = "('%(name)s', %(type)s, '%(address)s', %(port)s, %(orgStructure_id)s, %(eQueueType_id)s)"
            valuesPart = ', '.join([valuesStatementTemplate % values for values in valuesList])

            if not query.exec_(insertStmtTemplate % valuesPart):
                CDatabase.checkDatabaseError(query.lastError(), query.lastQuery())

        query = QtSql.QSqlQuery(self._db)
        deleteCond = '(address, port) NOT IN (%s)' % ', '.join(deleteCondPartList) if deleteCondPartList else '1'
        if not query.exec_('''DELETE FROM EQHost WHERE type = %s AND %s''' % (CEQController.EQHost.Control, deleteCond)):
            CDatabase.checkDatabaseError(query.lastError(), query.lastQuery())




    @classmethod
    # def __new__(cls, *args, **kwargs):
    def getInstance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = CEQController(*args, **kwargs)
        return cls._instance


    def controlModel(self):
        return self._controlModel


    def isWork(self):
        return self._updateModelsTimerId is not None


    def setAutoUpdateTimer(self, seconds = None):
        isWorkBefore = self.isWork()
        if self._updateModelsTimerId is not None:
            self.killTimer(self._updateModelsTimerId)
        if seconds is None:
            self._updateModelsTimerId = None
        else:
            self._updateModelsTimerId = self.startTimer(seconds * 1000)
        self.workStateChanged.emit(self.isWork())
        if self.isWork() and not isWorkBefore:
            self.workStarted.emit()
        if not self.isWork() and isWorkBefore:
            self.workFinished.emit()


    def baseOrgStructureByControl(self, controlId):
        eQueueTypeId = self._controlModel.queueTypeId(controlId)
        return self.baseOrgStrcuture(eQueueTypeId)


    def baseOrgStrcuture(self, eQueueTypeId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        return model.baseOrgStructureId() if model else None



    def timerEvent(self, event):
        if event.timerId() == self._updateModelsTimerId:
            self.updateModels()


    @QtCore.pyqtSlot()
    def updateModels(self):
        activedQueueTypes = self.controlModel().activedQueueTypes()
        for queueTypeId, model in self._ticketModelByQueueTypeId.items():
            if queueTypeId in activedQueueTypes:
                if model.findInProgress():
                    for control in self._controlModel.controls(queueTypeId):
                        self._currentTicketIdForControl[control.controlId()] = model.findInProgress()
                model.select()
            else:
                model.resetNext()
                # model.finishAllTickets()


    def initNameResolvers(self):
        if self._db.isOpen():
            query = QtSql.QSqlQuery(self._db)
            query.exec_(u'''SELECT id, name FROM rbEQueueType''')
            while query.next():
                record = query.record()
                self._queueTypeNameResolver[record.value('id').toInt()[0]] = record.value('name').toString()

            if query.exec_(u'''SELECT id, name FROM OrgStructure'''):
                while query.next():
                    record = query.record()
                    self._orgStructureNameResolver[record.value('id').toInt()[0]] = record.value('name').toString()
            else:
                CDatabase.checkDatabaseError(query.lastError(), query.lastQuery())




    @QtCore.pyqtSlot(int, int, QtCore.QString, QtCore.QString, int)
    def addRemoteControl(self, orgStructureId, queueTypeId, name, host, port):
        control = CEQRemoteControl(host, port)
        self._controlModel.addControl(orgStructureId, queueTypeId, control, name)


    def removeControl(self, controlId):
        self._controlModel.removeControl(controlId)


    @QtCore.pyqtSlot(int)
    def onTicketStatusChanged(self, ticketId):
        # print ticketId #debug: atronah:
        #TODO: atronah: рассылка push-уведомлений на отображения
        self.ticketStatusChanged.emit(ticketId)


    @QtCore.pyqtSlot(int)
    def addQueueType(self, queueTypeId):
        if queueTypeId and not self._ticketModelByQueueTypeId.has_key(queueTypeId):
            ticketModel = CEQTicketControlModel(queueTypeId, self._db, self)
            # ticketModel.queueChanged.connect(self.onQueueChanged)

            ticketModel.prevValueChanged.connect(self._controlModel.changePrevValue)
            ticketModel.currentValueChanged.connect(self._controlModel.changeCurrentValue)
            ticketModel.nextValueChanged.connect(self._controlModel.changeNextValue)

            ticketModel.prevValueChanged.connect(self.updateControls)
            ticketModel.currentValueChanged.connect(self.updateControls)
            ticketModel.nextValueChanged.connect(self.updateControls)



            ticketModel.ticketStatusChanged.connect(self.onTicketStatusChanged)

            self._ticketModelByQueueTypeId[queueTypeId] = ticketModel
            self.updateModels()
        return self._ticketModelByQueueTypeId.get(queueTypeId, None)


    @QtCore.pyqtSlot(int)
    def removeQueueType(self, queueTypeId):
        if self._ticketModelByQueueTypeId.has_key(queueTypeId):
            ticketModel = self._ticketModelByQueueTypeId.pop(queueTypeId)

            ticketModel.prevValueChanged.disconnect(self._controlModel.changePrevValue)
            ticketModel.currentValueChanged.disconnect(self._controlModel.changeCurrentValue)
            ticketModel.nextValueChanged.disconnect(self._controlModel.changeNextValue)

            ticketModel.clear()


    @QtCore.pyqtSlot()
    def startWork(self):
        self.updateModels()
        self.setAutoUpdateTimer(self._updateTimeout)


    @QtCore.pyqtSlot()
    def stopWork(self):
        self.setAutoUpdateTimer(None)


    def processCallTicket(self, callType, controlId, isCurrentComplete = True, value = QtCore.QString()):
        control = self._controlModel.control(controlId)
        if control.currentState() != CAbstractEQControl.ActiveState:
            return

        queueTypeId = self._controlModel.queueTypeId(controlId)
        orgStructureId = self._controlModel.orgStructureId(controlId)
        model = self.getQueueTicketControlModel(queueTypeId)
        if model:
            ticketId = self._currentTicketIdForControl.get(controlId)
            ticketStatus = EQTicketStatus.Complete if isCurrentComplete else EQTicketStatus.Canceled
            if callType == self.PrevCallType:
                ticketId = model.moveToPrev(ticketStatus, ticketId)
            elif callType == self.ReCallType:
                ticketId = model.reCall(ticketId)
            elif callType == self.NextCallType:
                ticketId = model.moveToNext(currentStatus = ticketStatus,
                                            orgStructurId = orgStructureId,
                                            currentTicketId = ticketId)
            elif callType == self.CustomCallType:
                ticketId = model.moveToNext(currentStatus = ticketStatus,
                                            orgStructurId = orgStructureId,
                                            currentTicketId = ticketId,
                                            value = value)
            else:
                return False
            if ticketId:
                self._currentTicketIdForControl[controlId] = ticketId
            self.updateButtonsState(controlId)
        return False


    def getQueueTicketControlModel(self, eQueueTypeId):
        if not eQueueTypeId:
            return None

        model = self._ticketModelByQueueTypeId.get(eQueueTypeId, None)
        if not model:
            model = self.addQueueType(eQueueTypeId)
        return model


    @QtCore.pyqtSlot(int, int, int)
    def summon(self, eQueueTypeId, eqTicketId, orgStructureId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        if model:
            model.summon(eqTicketId, orgStructureId if orgStructureId else None, pushCurrentToPrev = False)
            model.select()


    @QtCore.pyqtSlot(int, int)
    def markAsEmergency(self, eQueueTypeId, eqTicketId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        if model:
            model.markAsEmergency(eqTicketId)


    @QtCore.pyqtSlot(int, int)
    def markAsCompleted(self, eQueueTypeId, eqTicketId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        if model:
            model.finishTicket(EQTicketStatus.Complete, eqTicketId)


    @QtCore.pyqtSlot(int, int)
    def markAsCanceled(self, eQueueTypeId, eqTicketId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        if model:
            model.finishTicket(EQTicketStatus.Canceled, eqTicketId)


    @QtCore.pyqtSlot(int, int)
    def markAsReady(self, eQueueTypeId, eqTicketId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        if model:
            model.markAsReady(eqTicketId)


    @QtCore.pyqtSlot(int, int)
    def markAsIssued(self, eQueueTypeId, eqTicketId):
        model = self.getQueueTicketControlModel(eQueueTypeId)
        if model:
            model.markAsIssued(eqTicketId)


    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, bool)
    def next(self, controlId, isCurrentComplete = True):
        self.processCallTicket(self.NextCallType, controlId, isCurrentComplete)




    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, bool)
    def prev(self, controlId, isCurrentComplete = True):
        self.processCallTicket(self.PrevCallType, controlId, isCurrentComplete)



    @QtCore.pyqtSlot(int, QtCore.QString)
    @QtCore.pyqtSlot(int, QtCore.QString, bool)
    def custom(self, controlId, value, isCurrentComplete = True):
        self.processCallTicket(self.CustomCallType, controlId, isCurrentComplete, value)


    @QtCore.pyqtSlot(int)
    def reCall(self, controlId):
        self.processCallTicket(self.ReCallType, controlId)


    @QtCore.pyqtSlot()
    def openSettings(self, parent = None):
        if self._settingsWindow is None:
            self._settingsWindow = CEQSettingsWindow(parent)
            self._settingsWindow.setControlModel(self.controlModel())

            self._settingsWindow.addedControl.connect(self.addRemoteControl)
            self._settingsWindow.allControlsEnabled.connect(self.controlModel().enableControls)
            self._settingsWindow.allControlsDisabled.connect(self.controlModel().disableControls)

            self._settingsWindow.loadControlsClicked.connect(self.loadControls)
            self._settingsWindow.saveControlsClicked.connect(self.saveControls)

            self.workStateChanged.connect(self._settingsWindow.changeWorkState)

        self._settingsWindow.setAutoStart(self.isAutoStart())
        result = self._settingsWindow.exec_()
        self.setAutoStart(self._settingsWindow.isAutoStart())
        return result


    @classmethod
    def isAutoStart(cls):
        return cls._isAutoStart


    @classmethod
    def setAutoStart(cls, isAutoStart):
        cls._isAutoStart = isAutoStart



    @QtCore.pyqtSlot()
    def onControlActivated(self):
        self.updateModels()


    def updateControls(self, queueTypeId):
        # print 'update controls' #debug: atronah:
        for control in self._controlModel.controls(queueTypeId):
            self.updateButtonsState(control.controlId())


    @QtCore.pyqtSlot(int)
    def updateButtonsState(self, controlId):
        state = CAbstractEQControl.ControlButtonsState.AllDiasabled
        queueTypeId = self._controlModel.queueTypeId(controlId)
        model = self._ticketModelByQueueTypeId.get(queueTypeId, None)
        if model:
            control = self._controlModel.control(controlId)
            if self._controlModel.orgStructureId(controlId):
                if control.currentState() == CAbstractEQControl.ActiveState:
                    state |= CAbstractEQControl.ControlButtonsState.StopEnabled
                    if model.currentIdList() or model.status(model.nextId()) in [EQTicketStatus.Ready, EQTicketStatus.Emergency]:
                        state |= CAbstractEQControl.ControlButtonsState.NextEnabled
                    currentId = self._currentTicketIdForControl.get(controlId, None)
                    if currentId in model.currentIdList():
                        state |= CAbstractEQControl.ControlButtonsState.ReCallEnabled
                elif control.currentState() == CAbstractEQControl.EnabledState:
                    state |= CAbstractEQControl.ControlButtonsState.StartEnabled
        self._controlModel.updateButtonsState(controlId, state)


    # @QtCore.pyqtSlot(int)
    # def onQueueChanged(self, queueTypeId):
    #     pass


#==========================================================================




def main():
    import sys
    from PyQt4 import QtGui
    from library.database import connectDataBase

    app = QtGui.QApplication(sys.argv)

    connectionName = generalConnectionName()
    db = connectDataBase('MYSQL',
                             #'127.0.0.1',
                             '192.168.0.3',
                             3306,
                             'b15',
                             'dbuser',
                             'dbpassword',
                             connectionName)
    # query = QtSql.QSqlQuery(db.db)
    # query.exec_(u'''UPDATE EQueue
    #                     INNER JOIN rbEQueueType ON rbEQueueType.id = EQueue.eQueueType_id
    #                 SET EQueue.date = CURRENT_DATE()
    #                 WHERE rbEQueueType.code like 'unittest' ''')
    # query.exec_(u'''UPDATE EQueueTicket
    #                     INNER JOIN EQueue ON EQueue.id = EQueueTicket.queue_id
    #                     INNER JOIN rbEQueueType ON rbEQueueType.id = EQueue.eQueueType_id
    #                 SET EQueueTicket.status = 0
    #                 WHERE EQueue.date = CURRENT_DATE
    #                       AND rbEQueueType.code like 'unittest'
    #                       AND EQueueTicket.value like 'rsrv%' ''')
    # query.exec_(u'''UPDATE EQueueTicket
    #                     INNER JOIN EQueue ON EQueue.id = EQueueTicket.queue_id
    #                     INNER JOIN rbEQueueType ON rbEQueueType.id = EQueue.eQueueType_id
    #                 SET EQueueTicket.status = 2
    #                 WHERE EQueue.date = CURRENT_DATE
    #                       AND rbEQueueType.code like 'unittest'
    #                       AND (EQueueTicket.value like 'prgs%' OR EQueueTicket.value like 'smn%') ''')
    # query.exec_(u'''UPDATE EQueueTicket
    #                     INNER JOIN EQueue ON EQueue.id = EQueueTicket.queue_id
    #                     INNER JOIN rbEQueueType ON rbEQueueType.id = EQueue.eQueueType_id
    #                 SET EQueueTicket.status = 1
    #                 WHERE EQueue.date = CURRENT_DATE
    #                       AND rbEQueueType.code like 'unittest'
    #                       AND EQueueTicket.value like 'wait%' ''')
    # query.exec_(u'''UPDATE EQueueTicket
    #                     INNER JOIN EQueue ON EQueue.id = EQueueTicket.queue_id
    #                     INNER JOIN rbEQueueType ON rbEQueueType.id = EQueue.eQueueType_id
    #                 SET EQueueTicket.summonDatetime = NOW()
    #                 WHERE EQueue.date = CURRENT_DATE
    #                       AND rbEQueueType.code like 'unittest'
    #                       AND EQueueTicket.value like 'smn%' ''')
    # eqController = CEQController.getInstance(connectionName)
    # eqController.openSettings()


    model = QtSql.QSqlTableModel(db = db.db)
    model.setTable(u'Action')
    model.setSort(2, QtCore.Qt.AscendingOrder)
    import re
    print '-', re.findall(ur'ORDER\s+BY\s+(.+)', unicode(model.orderByClause()))

    sys.exit(1)

    sys.exit(0)



if __name__ == '__main__':
    main()




