# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils           import getWorkEventTypeFilter
from Events.EditDispatcher  import getEventFormClass

from library.Utils          import forceInt, forceRef, forceString
from Reports.Report         import normalizeMKB

from Ui_LogicalControlMesDialog import Ui_LogicalControlMesDialog


class CLogicalControlMes(QtGui.QDialog, Ui_LogicalControlMesDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.cmbEventProfile.setTable('rbEventProfile', True)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        if QtGui.qApp.userSpecialityId:
            self.cmbPerson.setValue(QtGui.qApp.userId)
            self.cmbSpeciality.setValue(QtGui.qApp.userSpecialityId)
        self.abortProcess = False
        self.checkRun = False
        self.recordBuffer = {}
        self.eventIdList = []
        self.recordBufferCorrect = []
        self.rows = 0
        self.errorList = [u'отсутствует МЭС', u'не соответствует длительность события требованию МЭС', u'не соответствует заключительный диагноз требованию МЭС', u'Не выполнена альтернативность выбора услуг', u'не соответствует количество визитов требованию МЭС', u'не соответствие выполненных действий с ЧП=1 по требованию МЭС']
        self.cmbMes._popup.setCheckBoxes('logicalControlMes')


    @QtCore.pyqtSlot()
    def on_btnEndControl_clicked(self):
        if self.checkRun:
            self.abortProcess = True
            self.listResultControlMes.reset()
            self.lblCountLine.setText(u'всего строк: %d' % self.listResultControlMes.count())
        else:
            self.close()
            QtGui.qApp.emitCurrentClientInfoChanged()


    @QtCore.pyqtSlot()
    def on_btnStartControl_clicked(self):
        try:
            self.lblCountLine.setText(u'всего строк: 0')
            self.prbControlMes.setFormat('%v')
            self.prbControlMes.setValue(0)
            self.loadDataMes()
        finally:
            self.checkRun = False
            self.abortProcess = False

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)


    @QtCore.pyqtSlot(int)
    def on_cmbEventProfile_currentIndexChanged(self, index):
        self.cmbMes.setEventProfile(self.cmbEventProfile.value())


    @QtCore.pyqtSlot(int)
    def on_cmbEventFeature_currentIndexChanged(self, index):
        if self.cmbEventFeature.currentIndex() != 2:
            self.chkCountVisits.setEnabled(True)
            self.chkExecActions.setEnabled(True)
        else:
            self.chkCountVisits.setChecked(False)
            self.chkCountVisits.setEnabled(False)
            self.chkExecActions.setChecked(False)
            self.chkExecActions.setEnabled(False)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_listResultControlMes_doubleClicked(self, index):
        row = self.listResultControlMes.currentRow()
        eventId = self.eventIdList[row]
        if eventId:
            formClass = getEventFormClass(eventId)
            dialog = formClass(self)
            dialog.load(eventId)
            dialog.exec_()


    def loadDataMes(self):
        self.recordBuffer = {}
        self.eventIdList = []
        self.recordBufferCorrect = []
        self.listResultControlMes.checkRunListWidget = False
        self.listResultControlMes.selectAll()
        self.listResultControlMes.clear()
        self.rows = 0
        self.lblCountLine.setText(u'всего строк: 0')
        self.prbControlMes.setFormat('%v')
        self.prbControlMes.setValue(0)
        self.btnEndControl.setText(u'прервать')
        self.btnStartControl.setEnabled(False)
        try:
            QtGui.qApp.callWithWaitCursor(self, self.controlEventMes)
            self.lblCountLine.setText(u'всего строк: %d' % len(self.recordBuffer))
            lenStr = self.selectDataEvent()
        except Exception, e:
           self.abortProcess = True
        if self.abortProcess:
            self.listResultControlMes.reset()
            self.lblCountLine.setText(u'всего строк: %d' % self.listResultControlMes.count())
        self.prbControlMes.setText(u'прервано' if self.abortProcess else u'готово')
        self.btnEndControl.setText(u'закрыть')
        self.btnStartControl.setEnabled(True)
        self.checkRun = False
        self.abortProcess = False
        self.listResultControlMes.recordBufferCorrectLW = self.recordBufferCorrect
        self.listResultControlMes.checkRunListWidget = True


    def printDataDiagnosis(self, valStr):
        self.errorStr = u''
        self.listResultControlMes.addItem(self.errorStr + valStr)
        item = self.listResultControlMes.item(self.rows)
        self.listResultControlMes.scrollToItem(item)
        self.rows += 1


    def selectDataEvent(self):
        prbControlPercent = 0
        self.eventIdList = []
        lenStr = len(self.recordBuffer)
        if lenStr > 1:
            self.prbControlMes.setMaximum(lenStr - 1)
        i = 0
        for record, error in self.recordBuffer.values():
            QtGui.qApp.processEvents()
            if self.abortProcess:
                self.checkRun = False
                break
            self.prbControlMes.setValue(prbControlPercent)
            prbControlPercent += 1
            eventId  = forceRef(record.value('id'))
            self.eventIdList.append(eventId)
            setDate  = forceString(record.value('setDate'))
            execDate  = forceString(record.value('execDate'))
            eventTypeName  = forceString(record.value('eventTypeName'))
            person  = forceString(record.value('personName'))
            MKB = normalizeMKB(forceString(record.value('MKB')))
            self.createStrEvent(forceString(eventId), eventTypeName, person, setDate, execDate, MKB, error)
            i += 1
        return lenStr


    def createStrEvent(self, eventId, eventType, person, setDate, execDate, MKB, error):
        resultStr = u''
        resultStr += u'событие %s, тип %s, специалист %s, период %s - %s, диагноз %s, ошибка %s'%(eventId, eventType, person, setDate, execDate, MKB, error)
        self.printDataDiagnosis(resultStr)


    def controlEventMes(self):
        self.checkRun = True
        begDate = self.dateBeginPeriod.date()
        endDate = self.dateEndPeriod.date()
        mesId = self.cmbMes.value()
        eventProfileId = self.cmbEventProfile.value()
        eventPurposeId = self.cmbEventPurpose.value()
        eventTypeId = self.cmbEventType.value()
        orgStructureId = self.cmbOrgStructure.value()
        specialityId = self.cmbSpeciality.value()
        personId = self.cmbPerson.value()
        eventExec = self.cmbEventExec.currentIndex()
        eventFeature = self.cmbEventFeature.currentIndex()
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tablePerson = db.table('vrbPersonWithSpeciality')
        tableMES = db.table('mes.MES')
        tableMESMKB = db.table('mes.MES_mkb')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')
        tableRBDiagnosisType = db.table('rbDiagnosisType')
        tableRBMesSpecification = db.table('rbMesSpecification')
        cols = [tableEvent['id'],
                tableEvent['MES_id'],
                tableEvent['setDate'],
                tableEvent['execDate'],
                tableEventType['code'],
                tableEventType['name'].alias('eventTypeName'),
                tablePerson['name'].alias('personName'),
                tableDiagnosis['MKB']
                ]
        # FIXME: Действительно ли mesRequired должно срвниваться с 1? По логике сейчас МЭС обязателен при любом ненулевом значении.
        cond = [tableEvent['deleted'].eq(0),
                tableEventType['deleted'].eq(0),
                tableEventType['mesRequired'].eq(1)
                ]
        if mesId:
            cond.append(tableEvent['MES_id'].eq(mesId))
        if eventProfileId:
            cond.append(tableEventType['eventProfile_id'].eq(eventProfileId))
        if eventPurposeId:
            cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
        if eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(eventTypeId))
        if orgStructureId:
            cond.append(tablePerson['orgStructure_id'].eq(orgStructureId))
        if specialityId:
            cond.append(tablePerson['speciality_id'].eq(specialityId))
        if personId:
            cond.append(tablePerson['id'].eq(personId))
        if eventExec == 1:
            cond.append(tableEvent['execDate'].isNotNull())
        elif eventExec == 2:
            cond.append(tableEvent['execDate'].isNull())
        if eventFeature == 1:
            cond.append(tableRBMesSpecification['done'].eq(1))
        elif eventFeature == 2:
            cond.append(tableRBMesSpecification['done'].eq(0))
        if begDate:
            cond.append(tableEvent['setDate'].isNotNull())
            cond.append(tableEvent['setDate'].dateGe(begDate))
        if endDate:
            cond.append(tableEvent['setDate'].isNotNull())
            cond.append(tableEvent['setDate'].dateLe(endDate))
        cond.append(u'''rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1)))''')
        cond.append(u'''(Diagnostic.id IS NULL OR Diagnostic.deleted = 0) AND (Diagnosis.id IS NULL OR Diagnosis.deleted = 0)''')
        table = tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tablePerson, tableEvent['execPerson_id'].eq(tablePerson['id']))
        if eventFeature > 0:
            table = table.innerJoin(tableRBMesSpecification, tableEvent['mesSpecification_id'].eq(tableRBMesSpecification['id']))
        table = table.leftJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
        table = table.leftJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
        table = table.leftJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))

        if self.chkMes.isChecked():
            condNotMES = self.getCond(cond)
            condNotMES.append(tableEvent['MES_id'].isNull())
            stmt = db.selectStmt(table, cols, condNotMES, order = u'Event.id')
            self.getDataRecords(stmt, 0)
        if self.chkDuration.isChecked():
            condDuration = self.getCond(cond)
            tablequeryMES = table.innerJoin(tableMES, tableEvent['MES_id'].eq(tableMES['id']))
            currentDateTime = tableEvent['execDate'].formatValue(QtCore.QDateTime.currentDateTime())
            condDuration.append(tableMES['deleted'].eq(0))
            condDuration.append(u'''(Event.execDate IS NULL AND %s >= Event.setDate) AND (DATEDIFF(IF(Event.execDate IS NOT NULL, IF(Event.execDate != Event.setDate, Event.execDate, ADDDATE(Event.execDate, 1)), IF(%s != Event.setDate, %s, ADDDATE(%s, 1))), Event.setDate) < mes.MES.minDuration OR DATEDIFF(IF(Event.execDate IS NOT NULL, IF(Event.execDate != Event.setDate, Event.execDate, ADDDATE(Event.execDate, 1)), IF(%s != Event.setDate, %s, ADDDATE(%s, 1))), Event.setDate) > mes.MES.maxDuration)'''%(currentDateTime, currentDateTime, currentDateTime, currentDateTime, currentDateTime, currentDateTime, currentDateTime))
            stmt = db.selectStmt(tablequeryMES, cols, condDuration, order = u'Event.id')
            self.getDataRecords(stmt, 1)
        if self.chkMKB.isChecked():
            condMESMKB = self.getCond(cond)
            condMESMKB.append(u'''Event.MES_id IS NOT NULL AND Diagnosis.id IS NOT NULL AND Diagnosis.MKB NOT IN (SELECT mes.MES_mkb.mkb FROM mes.MES_mkb WHERE mes.MES_mkb.master_id = Event.MES_id AND mes.MES_mkb.deleted = 0)''')
            stmt = db.selectStmt(table, cols, condMESMKB, order = u'Event.id')
            self.getDataRecords(stmt, 2)
        if self.chkNotAlternative.isChecked():
            condNotAlternative = self.getCond(cond)
            condNotAlternative.append(tableEvent['MES_id'].isNotNull())
            stmt = db.selectStmt(table, cols, condNotAlternative, order = u'Event.id')
            self.getDataRecordActionAlternativeErrors(stmt, 3)
        if self.chkCountVisits.isChecked() and eventFeature != 2:
            condCountVisits = self.getCond(cond)
            condCountVisits.append(tableEvent['MES_id'].isNotNull())
            condCountVisits.append(tableEvent['execDate'].isNotNull())
            stmt = db.selectStmt(table, cols, condCountVisits, order = u'Event.id')
            self.getDataRecordVisitErrors(stmt, 4)
        if self.chkExecActions.isChecked():
            condExecActions = self.getCond(cond)
            condExecActions.append(tableEvent['MES_id'].isNotNull())
            condExecActions.append(tableEvent['execDate'].isNotNull())
            stmt = db.selectStmt(table, cols, condExecActions, order = u'Event.id')
            self.getDataRecordActionErrors(stmt, 5)


    def getCond(self, conds):
        newCond = []
        for cond in conds:
            newCond.append(cond)
        return newCond


    def getDataRecords(self, stmt, indexError):
        query = QtGui.qApp.db.query(stmt)
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('id'))
            if not self.recordBuffer.get((eventId, indexError), None):
                self.recordBuffer[(eventId, indexError)] = (record, self.errorList[indexError])


    def getDataRecordVisitErrors(self, stmt, indexError):
        query = QtGui.qApp.db.query(stmt)
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('id'))
            mesId = forceRef(record.value('MES_id'))
            groupAvailable, visitTypeErr = self.getMesAmountVisitErrors(eventId, mesId)
            countedVisitErr = 0
            for available in groupAvailable.values():
                if available != 0:
                    countedVisitErr = 1
                    break
            if (countedVisitErr or visitTypeErr) and (not self.recordBuffer.get((eventId, indexError), None)):
                self.recordBuffer[(eventId, indexError)] = (record, self.errorList[indexError])


    def getDataRecordActionAlternativeErrors(self, stmt, indexError):
        groupIdList = []
        codes = [u'в',
                 u'к',
                 u'д',
                 u'л',
                 u'с',
                 u'э']
        query = QtGui.qApp.db.query(stmt)
        for code in codes:
            groupId = forceRef(QtGui.qApp.db.translate('mes.mrbServiceGroup', 'code', code, 'id'))
            if groupId and groupId not in groupIdList:
               groupIdList.append(groupId)
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('id'))
            mesId = forceRef(record.value('MES_id'))
            countedActionErr = 0
            groupAlternativeList = []
            for groupId in groupIdList:
                if not countedActionErr and eventId and mesId:
                    mesActionaverageQnt = self.getMesAmountActionTypeAlternative(eventId, mesId, groupId)
                    for key, item in mesActionaverageQnt.items():
                        countActions, groupAlternative = item
                        if countActions and groupAlternative and (groupAlternative not in groupAlternativeList):
                            groupAlternativeList.append(groupAlternative)
                        elif countActions and groupAlternative in groupAlternativeList:
                            countedActionErr = True
                            break
            if countedActionErr and (not self.recordBuffer.get((eventId, indexError), None)):
                self.recordBuffer[(eventId, indexError)] = (record, self.errorList[indexError])


    def getMesAmountActionTypeAlternative(self, eventId, mesId, groupId):
        result = 0
        db = QtGui.qApp.db
        stmt = u'''
            SELECT
            mMS.id AS mesActionId,
            ActionType.id AS actionTypeId,
            mMS.groupCode AS groupAlternative,
            ActionType.amount,
            mMS.averageQnt
            FROM Action
            INNER JOIN ActionType ON Action.actionType_id = ActionType.id
            INNER JOIN rbService  ON rbService.id = ActionType.nomenclativeService_id
            INNER JOIN mes.mrbService  AS mSV ON rbService.code = mSV.code
            LEFT JOIN mes.MES_service AS mMS ON mMS.service_id = mSV.id
            WHERE ActionType.deleted = 0 AND mMS.deleted = 0 AND mSV.deleted = 0  AND Action.event_id = %d AND mMS.master_id = %d AND mSV.group_id = %d AND mMS.necessity >= 1
            ORDER BY groupAlternative, mSV.code, mSV.name, mSV.id
        ''' % (eventId, mesId, groupId)

        query = db.query(stmt)
        mesActionaverageQnt = {}
        while query.next():
            record = query.record()
            mesActionId = forceRef(record.value('mesActionId'))
            groupAlternativeNew = forceRef(record.value('groupAlternative'))
            amount = forceInt(record.value('amount'))
            available, groupAlternative = mesActionaverageQnt.get(mesActionId, (0, None))
            mesActionaverageQnt[mesActionId] = (available + amount, groupAlternative if (not groupAlternativeNew and groupAlternative) else groupAlternativeNew)
        return mesActionaverageQnt


    def getDataRecordActionErrors(self, stmt, indexError):
        groupIdList = []
        codes = [u'в',
                 u'к',
                 u'д',
                 u'л',
                 u'с',
                 u'э']
        query = QtGui.qApp.db.query(stmt)
        for code in codes:
            groupId = forceRef(QtGui.qApp.db.translate('mes.mrbServiceGroup', 'code', code, 'id'))
            if groupId and groupId not in groupIdList:
               groupIdList.append(groupId)
        groupAlternativeList = []
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('id'))
            mesId = forceRef(record.value('MES_id'))
            countedActionErr = 0
            for groupId in groupIdList:
                if not countedActionErr and eventId and mesId:
                    mesActionaverageQnt = self.getMesAmountActionType(eventId, mesId, groupId)
                    stmtMES = '''
                        SELECT mrbService.code, mrbService.name, MES_service.averageQnt, MES_service.necessity, mrbService.doctorWTU, mrbService.paramedicalWTU, MES_service.id AS mesServiceId, MES_service.groupCode AS groupAlternative
                        FROM mes.mrbService
                        LEFT JOIN mes.MES_service ON MES_service.service_id = mrbService.id
                        WHERE MES_service.master_id=%d AND MES_service.deleted = 0 AND mrbService.deleted = 0 AND mrbService.group_id = %d AND MES_service.necessity >= 1
                        GROUP BY mrbService.code
                        ORDER BY mrbService.code, mrbService.name, mrbService.id
                        ''' % (mesId, groupId)
                    queryMES = QtGui.qApp.db.query(stmtMES)
                    countedActionErr = False
                    while queryMES.next():
                        recordMES = queryMES.record()
                        averageQnt = forceInt(recordMES.value('averageQnt'))
                        mesServiceId = forceInt(recordMES.value('mesServiceId'))
                        groupAlternativeNew = forceInt(record.value('groupAlternative'))
                        if mesServiceId in mesActionaverageQnt.keys():
                            actionaverage, groupAlternative = mesActionaverageQnt.get(mesServiceId, (None, None))
                        else:
                            actionaverage = 0
                            groupAlternative = groupAlternativeNew
                        if actionaverage == None and (not groupAlternative or (groupAlternative not in groupAlternativeList)):
                            countedActionErr = True
                            break
                        elif actionaverage != 0:
                            if groupAlternative and (groupAlternative not in groupAlternativeList):
                                groupAlternativeList.append(groupAlternative)
                            countedActionErr = True
                            break
                        elif groupAlternative and (groupAlternative not in groupAlternativeList):
                            groupAlternativeList.append(groupAlternative)
            if countedActionErr and (not self.recordBuffer.get((eventId, indexError), None)):
                self.recordBuffer[(eventId, indexError)] = (record, self.errorList[indexError])


    def getMesAmountVisitErrors(self, eventId, mesId):
        result = 0
        db = QtGui.qApp.db
        stmt = u'''
            SELECT
            mMV.groupCode  AS prvsGroup,
            mMV.averageQnt AS averageQnt,
            Visit.id       AS visitId,
            IF(mMV.visitType_id=mVT.id, 0, 1) AS visitTypeErr
            FROM Visit
            LEFT JOIN Person ON Person.id  = Visit.person_id
            LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
            LEFT JOIN rbVisitType  ON rbVisitType.id = Visit.visitType_id
            LEFT JOIN mes.mrbVisitType  AS mVT  ON rbVisitType.code = mVT.code
            LEFT JOIN mes.mrbSpeciality AS mS   ON mS.regionalCode = rbSpeciality.regionalCode
            LEFT JOIN mes.MES_visit     AS mMV  ON mMV.speciality_id = mS.id
            WHERE Visit.deleted = 0 AND mMV.deleted = 0 AND mS.deleted = 0 AND mVT.deleted = 0 AND Visit.event_id = %d AND mMV.master_id = %d
            ORDER BY visitTypeErr, mMV.groupCode, Visit.date
        ''' % (eventId, mesId)

        query = db.query(stmt)
        groupAvailable = {}
        countedVisits = set()
        visitTypeErr = 0
        while query.next():
            record = query.record()
            visitId = forceRef(record.value('visitId'))
            visitTypeError = forceInt(record.value('visitTypeErr'))
            visitTypeErr += visitTypeError
            if not visitTypeError and (visitId not in countedVisits):
                prvsGroup = forceInt(record.value('prvsGroup'))
                averageQnt = forceInt(record.value('averageQnt'))
                available = groupAvailable.get(prvsGroup, averageQnt)
                groupAvailable[prvsGroup] = available - 1
                countedVisits.add(visitId)
        return groupAvailable, visitTypeErr


    def getMesAmountActionType(self, eventId, mesId, groupId):
        result = 0
        db = QtGui.qApp.db
        stmt = u'''
            SELECT
            mMS.id AS mesActionId,
            mMS.groupCode AS groupAlternative,
            ActionType.id AS actionTypeId,
            ActionType.amount,
            mMS.averageQnt
            FROM Action
            INNER JOIN ActionType ON Action.actionType_id = ActionType.id
            INNER JOIN rbService  ON rbService.id = ActionType.nomenclativeService_id
            INNER JOIN mes.mrbService  AS mSV ON rbService.code = mSV.code
            LEFT JOIN mes.MES_service AS mMS ON mMS.service_id = mSV.id
            WHERE ActionType.deleted = 0 AND mMS.deleted = 0 AND mSV.deleted = 0  AND Action.event_id = %d AND mMS.master_id = %d AND mSV.group_id = %d AND mMS.necessity >= 1
            ORDER BY groupAlternative, mSV.code, mSV.name, mSV.id
        ''' % (eventId, mesId, groupId)

        query = db.query(stmt)
        mesActionaverageQnt = {}
        while query.next():
            record = query.record()
            mesActionId = forceRef(record.value('mesActionId'))
            groupAlternativeNew = forceRef(record.value('groupAlternative'))
            amount = forceInt(record.value('amount'))
            averageQnt = forceInt(record.value('averageQnt'))
            available, groupAlternative = mesActionaverageQnt.get(mesActionId, (averageQnt, groupAlternativeNew))
            mesActionaverageQnt[mesActionId] = (available - amount, groupAlternative if (not groupAlternativeNew and groupAlternative) else groupAlternativeNew)
        return mesActionaverageQnt
