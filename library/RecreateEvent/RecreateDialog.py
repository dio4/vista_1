# -*- coding: utf-8 -*-
"""Исправление 'поломанных' случаев для счетов. январь-февраль 2017 года"""


#############################################################################
##
## Copyright (C) 2006-2017 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtGui, QtCore
from library.DialogBase import CDialogBase
from library.RecreateEvent.Ui_RecreateDialog import Ui_CRecreateDialog
from library.Utils import forceString, toVariant


class CRecreateDialog(CDialogBase, Ui_CRecreateDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

        self.edtSetDateFrom.setDate(QtCore.QDate(2017, 01, 01))
        self.edtSetDateTo.setDate(QtCore.QDate().currentDate())

    def recreateEvent_1(self):
        eventsList = []
        db = QtGui.qApp.db

        deletedFlag = '1' if self.chkDebug.isChecked() else '0'
        mesIdTerap = forceString(self.edtEvent1MesIdTerap.value()) if self.edtEvent1MesIdTerap.value() else u'NULL'
        mesIdVop = forceString(self.edtEvent1MesIdVop.value()) if self.edtEvent1MesIdVop.value() else u'NULL'
        mesIdPed = forceString(self.edtEvent1MesIdPed.value()) if self.edtEvent1MesIdPed.value() else u'NULL'

        oldEventsQuery = u"""
            SELECT DISTINCT
                e.id AS event_id,
                d.id AS diagnostic_id,
                d1.id AS diagnosis_id,
                v.id AS visit_id,
                v.person_id AS visitPersonId
            FROM
                Event e
                INNER JOIN Visit v ON e.id = v.event_id AND v.deleted = 0
                INNER JOIN Person p ON v.person_id = p.id
                INNER JOIN rbSpeciality s ON p.speciality_id = s.id
                INNER JOIN OrgStructure os ON p.orgStructure_id = os.id AND os.isArea <> 0
                INNER JOIN Diagnostic d ON d.event_id = e.id AND d.deleted = 0
                INNER JOIN Diagnosis d1 ON d.diagnosis_id = d1.id AND d.deleted = 0
            WHERE
                e.deleted = 0
                AND d.diagnosisType_id IN (1, 2)
                AND e.execDate >= '{begDate}' AND e.execDate <= '{endDate}'
                AND date(v.date) >= '2017-01-01'
                # AND e.execDate >= '2017-01-09' AND e.execDate <= '2017-01-11'
                AND e.eventType_id IN ({eventType})
                AND e.contract_id IN ({contractId})
                # AND e.eventType_id IN (50)
                # AND e.contract_id IN (69)
                AND v.scene_id IN (2, 3)
                AND (s.name LIKE 'Терапевт%%' OR s.name LIKE 'ВОП%%' OR s.name LIKE 'Врач ОП%%' OR s.name LIKE 'Педиатр%%')
                # AND EXISTS
                # (
                #    SELECT DISTINCT
                #       v1.event_id AS event_id,
                #       COUNT(v1.id)
                #     FROM
                #       Visit v1
                #     WHERE
                #       e.id = v1.event_id AND v1.deleted = 0
                #     GROUP BY v1.event_id
                #     HAVING COUNT(v1.id) > 1
                # )
            """

        oldEventsQuery = oldEventsQuery.replace(u'{begDate}', self.edtSetDateFrom.date().toString('yyyy-MM-dd'))
        oldEventsQuery = oldEventsQuery.replace(u'{endDate}', self.edtSetDateTo.date().toString('yyyy-MM-dd'))
        oldEventsQuery = oldEventsQuery.replace(u'{eventType}', self.edtEventItem.text())
        oldEventsQuery = oldEventsQuery.replace(u'{contractId}', self.edtContractsId.text())

        try:
            records = db.getRecordList(stmt=oldEventsQuery)
            if records:
                for x in records:
                    try:
                        createNewEvents = u"""
                            INSERT INTO Event (
                              createDatetime,
                              createPerson_id,
                              eventType_id, -- here
                              org_id,
                              client_id,
                              setDate,
                              setPerson_id,
                              execDate,
                              execPerson_id,
                              isPrimary,
                              `order`,
                              result_id,
                              payStatus,
                              pregnancyWeek,
                              MES_id,
                              totalCost,
                              goal_id,
                              clientPolicy_id,
                              deleted,
                              note,
                              contract_id
                            )
                            # VALUES
                              SELECT DISTINCT
                                CURRENT_TIMESTAMP,
                                e.createPerson_id,
                                {newEventType}, #176, # 105, # 176, # e1.eventType_id,
                                e.org_id,
                                e.client_id,
                                v.date, # e.setDate,
                                e.setPerson_id,
                                v.date, # e.execDate,
                                %s, # e.execPerson_id,
                                e.isPrimary,
                                e.`order`,
                                {result_id}, # e.result_id,
                                0, # e.payStatus,
                                e.pregnancyWeek,
                                # IF(s.name LIKE 'Терапевт', 2080, IF(s.name LIKE 'ВОП%%', 2074, NULL)) AS MES_id, # e1.MES_id,
                                IF(s.name LIKE 'Терапевт', {MES_id_terap}, IF(s.name LIKE 'ВОП%%' OR s.name LIKE 'Врач ОП%%', {MES_id_vop}, IF(s.name LIKE 'Педиатр%%', {MES_id_ped}, NULL))) AS MES_id, # e1.MES_id,
                                e.totalCost,
                                {goal_id}, # e.goal_id,
                                e.clientPolicy_id,
                                {deleted},
                                # concat('VM_TEST_QUERY. Old `event_id` = ', e.id),
                                '{eventCond}', # concat('VM_TEST_QUERY. Old `event_id` = ', e.id, '; `visit_id` = ', v.id),
                                {newContractId}
                              FROM
                                EVENT e
                                INNER JOIN Visit v ON e.id = v.event_id AND v.deleted = 0
                                INNER JOIN Person p ON v.person_id = p.id
                                INNER JOIN rbSpeciality s ON p.speciality_id = s.id
                                INNER JOIN OrgStructure os ON p.orgStructure_id = os.id AND os.isArea <> 0
                              WHERE
                                e.id = %s
                                AND v.id = %s
                            """
                        createNewDiagnostic = u"""
                            INSERT INTO Diagnostic (
                              createDatetime,

                              createPerson_id,
                              event_id, -- HERE
                              diagnosis_id, -- HERE
                              diagnosisType_id,
                              setDate,
                              endDate,
                              character_id,
                              stage_id,
                              dispanser_id,
                              sanatorium,
                              hospital,
                              speciality_id,
                              person_id,
                              healthGroup_id,
                              result_id,
                              deleted,
                              notes
                            )
                            # VALUES
                              SELECT DISTINCT
                                CURRENT_TIMESTAMP,
                                createPerson_id,
                                %s, # event_id, -- HERE
                                %s, # diagnosis_id, -- HERE
                                diagnosisType_id,
                                setDate,
                                endDate,
                                character_id,
                                stage_id,
                                dispanser_id,
                                sanatorium,
                                hospital,
                                speciality_id,
                                %s, # person_id,
                                healthGroup_id,
                                {result_id},
                                {deleted},
                                '{eventCond}' # concat('VM_TEST_QUERY. Old `diagnostic_id` = ', d.id)
                              FROM
                                Diagnostic d
                              WHERE
                                d.id = %s
                              LIMIT 1
                            """
                        createNewDiagnosis = u"""
                            INSERT INTO Diagnosis (
                              createDatetime,
                              modifyDatetime,
                              createPerson_id,
                              deleted,
                              client_id,
                              diagnosisType_id,
                              character_id,
                              MKB,
                              MKBEx,
                              morphologyMKB,
                              TNMS,
                              dispanser_id,
                              traumaType_id,
                              setDate,
                              endDate,
                              mod_id,
                              person_id,
                              tempEventId,
                              note
                            )
                           SELECT
                              CURRENT_TIMESTAMP,
                              CURRENT_TIMESTAMP,
                              createPerson_id,
                              {deleted},
                              client_id,
                              diagnosisType_id,
                              character_id,
                              MKB,
                              MKBEx,
                              morphologyMKB,
                              TNMS,
                              dispanser_id,
                              traumaType_id,
                              setDate,
                              endDate,
                              mod_id,
                              %s, # person_id,
                              tempEventId,
                              '{eventCond}'
                            FROM Diagnosis d WHERE d.id = %s
                            LIMIT 1
                            """
                        removeEmptyEvents = u"""
                            UPDATE
                              Event e
                            SET
                              e.deleted = 1
                            WHERE
                              e.deleted = 0
                              AND (e.note LIKE 'Create VM%' OR e.note LIKE 'VM_TEST%')
                              AND EXISTS
                              (
                                SELECT DISTINCT
                                  v1.event_id AS event_id,
                                  COUNT(v1.id)
                                FROM
                                  Visit v1
                                WHERE
                                  e.id = v1.event_id AND v1.deleted = 0
                                GROUP BY v1.event_id
                                HAVING COUNT(v1.id) = 0
                              )
                            """

                        createNewEvents = createNewEvents.replace(u'{newEventType}',
                                                                  forceString(self.edtEvent1TypeId.value()))
                        createNewEvents = createNewEvents.replace(u'{newContractId}',
                                                                  forceString(self.edtEvent1ContractId.value()))
                        createNewEvents = createNewEvents.replace(u'{result_id}',
                                                                  forceString(self.edtEvent1ResultId.value()))
                        createNewEvents = createNewEvents.replace(u'{goal_id}',
                                                                  forceString(self.edtEvent1GoalId.value()))
                        createNewEvents = createNewEvents.replace(u'{MES_id_terap}', mesIdTerap)
                        createNewEvents = createNewEvents.replace(u'{MES_id_vop}', mesIdVop)
                        createNewEvents = createNewEvents.replace(u'{MES_id_ped}', mesIdPed)

                        createNewDiagnostic = createNewDiagnostic.replace(u'{result_id}', forceString(
                            self.edtEvent1DiagnosticResultId.value()))

                        createNewEvents = createNewEvents.replace(u'{deleted}', deletedFlag)
                        createNewDiagnostic = createNewDiagnostic.replace(u'{deleted}', deletedFlag)
                        createNewDiagnosis = createNewDiagnosis.replace(u'{deleted}', deletedFlag)

                        visitPersonId = forceString(x.value('visitPersonId'))
                        eventId = forceString(x.value('event_id'))
                        diagnosisId = forceString(x.value('diagnosis_id'))
                        diagnosticId = forceString(x.value('diagnostic_id'))
                        visitId = forceString(x.value('visit_id'))

                        # this need for search id
                        eventCond = 'VM_TEST_QUERY. Old `event_id` = %s' % eventId + '; `visit_id` IN (%s)' % visitId

                        createNewEvents = createNewEvents.replace(u'{visitQueryList}', forceString(visitId))
                        createNewEvents = createNewEvents.replace(u'{eventCond}', eventCond)
                        queryEvent = db.query(
                            createNewEvents % (
                                visitPersonId,
                                eventId,
                                visitId
                            )
                        )
                        # this need for search id
                        # eventCond = 'VM_TEST_QUERY. Old `event_id` = %s' % eventId + '; `visit_id` IN (%s)' % visitId

                        createNewDiagnosis = createNewDiagnosis.replace(u'{eventCond}', eventCond)
                        queryDiagnosis = db.query(
                            createNewDiagnosis % (
                                visitPersonId,
                                diagnosisId
                            )
                        )

                        queryDiagnosis.next()
                        diagnosisRecord = db.getRecordEx(
                            table='Diagnosis',
                            cols='id',
                            where=[
                                'note LIKE \'%s%%\'' % eventCond,
                                'deleted = 0'
                            ]
                        )
                        if diagnosisRecord:
                            lastDiagnosisId = forceString(diagnosisRecord.value('id'))
                        else:
                            print u'Event.id = %s | Не найден новый диагноз, возможно эвент удален.' % eventId
                            continue

                        queryEvent.next()
                        eventRecord = db.getRecordEx(
                            table='Event',
                            cols='id',
                            where=[
                                'note LIKE \'%s%%\'' % eventCond,
                                'deleted = 0'
                            ]
                        )
                        if eventRecord:
                            lastEventId = forceString(eventRecord.value('id'))
                        else:
                            print u'Event.id = %s | Не найден новый эвент, возможно старый эвент удален.' % eventId
                            continue

                        createNewDiagnostic = createNewDiagnostic.replace(u'{eventCond}', eventCond)
                        queryDiagnostic = db.query(
                            createNewDiagnostic % (
                                lastEventId,
                                lastDiagnosisId,
                                visitPersonId,
                                diagnosticId
                            )
                        )

                        queryDiagnostic.next()
                        diagnosticRecord = db.getRecordEx(
                            table='Diagnostic',
                            cols='id',
                            where=[
                                'notes LIKE \'%s%%\'' % eventCond,
                                'deleted = 0'
                            ]
                        )
                        if diagnosticRecord:
                            lastDiagnosticId = forceString(diagnosticRecord.value('id'))
                        else:
                            print u'Event.id = %s | Не найден новый Diagnostic, возможно эвент удален.' % eventId
                            continue

                        eventsList.append(
                            {
                                'event_id': eventId,
                                'diagnostic_id': diagnosticId,
                                'diagnosis_id': diagnosisId,
                                'visit_id': visitId,
                                'visitPersonId': visitPersonId,
                                'newEvent_id': lastEventId,
                                'newDiagnosis_id': lastDiagnosisId,
                                'newDiagnostic_id': lastDiagnosticId,
                            }
                        )
                    except Exception as e:
                        print e

                for x in eventsList:
                    try:
                        if x['visit_id']:
                            cond = ['id = %s' % x['visit_id']]
                            visit = db.getRecordList(table='Visit', cols='*', where=cond)
                            if visit:
                                for y in visit:
                                    y.setValue('event_id', toVariant(x['newEvent_id']))
                                    y.setValue('payStatus', toVariant(0))
                                    db.insertOrUpdate('Visit', y)
                            else:
                                print u'Event.id = %s | Не найдены посещения, возможно эвент удален.' % x['event_id']
                                continue

                            cond = ['id = %s' % x['event_id']]
                            event = db.getRecordEx(table='Event', cols='*', where=cond)
                            if event:
                                note = 'Create VM_TEST_QUERY. Old `visit_id` = %s\n' % x['visit_id']
                                event.setValue('note', toVariant(note + forceString(event.value('note'))))
                                db.insertOrUpdate('Event', event)
                            else:
                                print u'Event.id = %s | Не найден старый эвент, возможно он удален.' % x['event_id']
                                continue
                    except Exception as e:
                        print e
                rm = db.query(removeEmptyEvents)
                rm.next()

                # QtGui.QMessageBox.information(
                #     self,
                #     u'Перевыставление обращении Event 1',
                #     u'Перевыставление завершено успешно.',
                #     QtGui.QMessageBox.Ok
                # )
            else:
                QtGui.QMessageBox.information(
                    self,
                    u'Перевыставление обращении Event 1',
                    u'Нет данных для перевыставления.',
                    QtGui.QMessageBox.Ok
                )
            print u'Block 1'
        except Exception as e:
            QtGui.QMessageBox.critical(
                self,
                u'Перевыставление обращении Event 1',
                u'Не удалось выполнить перевыставление: "%s"' % e,
                QtGui.QMessageBox.Close
            )

    def recreateEvent_2(self):
        eventsList = []
        db = QtGui.qApp.db

        deletedFlag = '1' if self.chkDebug.isChecked() else '0'
        # mesIdTerap = forceString(self.edtEvent2MesIdTerap.value()) if self.edtEvent2MesIdTerap.value() else u'NULL'
        # mesIdVop = forceString(self.edtEvent2MesIdVop.value()) if self.edtEvent2MesIdVop.value() else u'NULL'
        oldEventsQuery = u"""
            SELECT DISTINCT
                e.id AS event_id,
                d.id AS diagnostic_id,
                d1.id AS diagnosis_id,
                v.id AS visit_id,
                v.person_id AS visitPersonId
            FROM
                Event e
                INNER JOIN Visit v ON e.id = v.event_id AND v.deleted = 0
                INNER JOIN Person p ON v.person_id = p.id
                INNER JOIN rbSpeciality s ON p.speciality_id = s.id
                INNER JOIN OrgStructure os ON p.orgStructure_id = os.id AND os.isArea <> 0
                INNER JOIN Diagnostic d ON d.event_id = e.id AND d.deleted = 0
                INNER JOIN Diagnosis d1 ON d.diagnosis_id = d1.id AND d.deleted = 0
            WHERE
                e.deleted = 0
                AND d.diagnosisType_id IN (1, 2)
                AND e.execDate >= '{begDate}' AND e.execDate <= '{endDate}'
                AND date(v.date) >= '2017-01-01'
                # AND e.execDate >= '2017-01-09' AND e.execDate <= '2017-01-11'
                AND e.eventType_id IN ({eventType})
                AND e.contract_id IN ({contractId})
                # AND e.eventType_id IN (50)
                # AND e.contract_id IN (69)
                AND v.scene_id NOT IN (2, 3)
                AND (s.name LIKE 'Терапевт%%' OR s.name LIKE 'ВОП%%' OR s.name LIKE 'Врач ОП%%' OR s.name LIKE 'Педиатр%%')
                AND e.note NOT LIKE 'VM_TEST_QUERY%%'
                AND EXISTS
                (
                    SELECT DISTINCT
                      v1.event_id AS event_id,
                      COUNT(v1.id)
                    FROM
                      Visit v1
                    WHERE
                      e.id = v1.event_id AND v1.deleted = 0
                      AND v.person_id = v1.person_id
                    GROUP BY v1.event_id
                    HAVING COUNT(v1.id) = 1
                )
            """

        oldEventsQuery = oldEventsQuery.replace(u'{begDate}', self.edtSetDateFrom.date().toString('yyyy-MM-dd'))
        oldEventsQuery = oldEventsQuery.replace(u'{endDate}', self.edtSetDateTo.date().toString('yyyy-MM-dd'))
        oldEventsQuery = oldEventsQuery.replace(u'{eventType}', self.edtEventItem.text())
        oldEventsQuery = oldEventsQuery.replace(u'{contractId}', self.edtContractsId.text())

        try:
            records = db.getRecordList(stmt=oldEventsQuery)
            if records:
                for x in records:
                    try:
                        createNewEvents = u"""
                            INSERT INTO Event (
                              createDatetime,
                              createPerson_id,
                              eventType_id, -- here
                              org_id,
                              client_id,
                              setDate,
                              setPerson_id,
                              execDate,
                              execPerson_id,
                              isPrimary,
                              `order`,
                              result_id,
                              payStatus,
                              pregnancyWeek,
                              MES_id,
                              totalCost,
                              goal_id,
                              clientPolicy_id,
                              deleted,
                              note,
                              contract_id
                            )
                            # VALUES
                              SELECT DISTINCT
                                CURRENT_TIMESTAMP,
                                e.createPerson_id,
                                {newEventType}, #176, # 105, # 176, # e1.eventType_id,
                                e.org_id,
                                e.client_id,
                                v.date, # e.setDate,
                                e.setPerson_id,
                                v.date, # e.execDate,
                                %s, # e.execPerson_id,
                                e.isPrimary,
                                e.`order`,
                                {result_id}, # e.result_id,
                                0, # e.payStatus,
                                e.pregnancyWeek,
                                # IF(s.name LIKE 'Терапевт', 2080, IF(s.name LIKE 'ВОП%%', 2074, NULL)) AS MES_id, # e1.MES_id,
                                IF(s.name LIKE 'Терапевт', {MES_id_terap}, IF(s.name LIKE 'ВОП%%' OR s.name LIKE 'Врач ОП%%', {MES_id_vop}, IF(s.name LIKE 'Педиатр%%', {MES_id_ped}, NULL))) AS MES_id, # e1.MES_id,
                                e.totalCost,
                                {goal_id}, # e.goal_id,
                                e.clientPolicy_id,
                                {deleted},
                                # concat('VM_TEST_QUERY. Old `event_id` = ', e.id),
                                '{eventCond}', # concat('VM_TEST_QUERY. Old `event_id` = ', e.id, '; `visit_id` = ', v.id),
                                {newContractId}
                              FROM
                                EVENT e
                                INNER JOIN Visit v ON e.id = v.event_id AND v.deleted = 0
                                INNER JOIN Person p ON v.person_id = p.id
                                INNER JOIN rbSpeciality s ON p.speciality_id = s.id
                                INNER JOIN OrgStructure os ON p.orgStructure_id = os.id AND os.isArea <> 0
                              WHERE
                                e.id = %s
                                AND v.id = %s
                            """
                        createNewDiagnostic = u"""
                            INSERT INTO Diagnostic (
                              createDatetime,

                              createPerson_id,
                              event_id, -- HERE
                              diagnosis_id, -- HERE
                              diagnosisType_id,
                              setDate,
                              endDate,
                              character_id,
                              stage_id,
                              dispanser_id,
                              sanatorium,
                              hospital,
                              speciality_id,
                              person_id,
                              healthGroup_id,
                              result_id,
                              deleted,
                              notes
                            )
                            # VALUES
                              SELECT DISTINCT
                                CURRENT_TIMESTAMP,
                                createPerson_id,
                                %s, # event_id, -- HERE
                                %s, # diagnosis_id, -- HERE
                                diagnosisType_id,
                                setDate,
                                endDate,
                                character_id,
                                stage_id,
                                dispanser_id,
                                sanatorium,
                                hospital,
                                speciality_id,
                                %s, # person_id,
                                healthGroup_id,
                                {result_id},
                                {deleted},
                                '{eventCond}' # concat('VM_TEST_QUERY. Old `diagnostic_id` = ', d.id)
                              FROM
                                Diagnostic d
                              WHERE
                                d.id = %s
                              LIMIT 1
                            """
                        createNewDiagnosis = u"""
                            INSERT INTO Diagnosis (
                              createDatetime,
                              modifyDatetime,
                              createPerson_id,
                              deleted,
                              client_id,
                              diagnosisType_id,
                              character_id,
                              MKB,
                              MKBEx,
                              morphologyMKB,
                              TNMS,
                              dispanser_id,
                              traumaType_id,
                              setDate,
                              endDate,
                              mod_id,
                              person_id,
                              tempEventId,
                              note
                            )
                           SELECT
                              CURRENT_TIMESTAMP,
                              CURRENT_TIMESTAMP,
                              createPerson_id,
                              {deleted},
                              client_id,
                              diagnosisType_id,
                              character_id,
                              MKB,
                              MKBEx,
                              morphologyMKB,
                              TNMS,
                              dispanser_id,
                              traumaType_id,
                              setDate,
                              endDate,
                              mod_id,
                              %s, # person_id,
                              tempEventId,
                              '{eventCond}'
                            FROM Diagnosis d WHERE d.id = %s
                            LIMIT 1
                            """
                        removeEmptyEvents = u"""
                            UPDATE
                              Event e
                            SET
                              e.deleted = 1
                            WHERE
                              e.deleted = 0
                              AND (e.note LIKE 'Create VM%' OR e.note LIKE 'VM_TEST%')
                              AND EXISTS
                              (
                                SELECT DISTINCT
                                  v1.event_id AS event_id,
                                  COUNT(v1.id)
                                FROM
                                  Visit v1
                                WHERE
                                  e.id = v1.event_id AND v1.deleted = 0
                                GROUP BY v1.event_id
                                HAVING COUNT(v1.id) = 0
                              )
                            """

                        createNewEvents = createNewEvents.replace(u'{newEventType}',
                                                                  forceString(self.edtEvent2TypeId.value()))
                        createNewEvents = createNewEvents.replace(u'{newContractId}',
                                                                  forceString(self.edtEvent2ContractId.value()))
                        createNewEvents = createNewEvents.replace(u'{result_id}',
                                                                  forceString(self.edtEvent2ResultId.value()))
                        createNewEvents = createNewEvents.replace(u'{goal_id}',
                                                                  forceString(self.edtEvent2GoalId.value()))
                        createNewEvents = createNewEvents.replace(u'{MES_id_terap}', u'NULL')  # mesIdTerap)
                        createNewEvents = createNewEvents.replace(u'{MES_id_vop}', u'NULL')  # mesIdVop)
                        createNewEvents = createNewEvents.replace(u'{MES_id_ped}', u'NULL')

                        createNewDiagnostic = createNewDiagnostic.replace(u'{result_id}', forceString(
                            self.edtEvent2DiagnosticResultId.value()))

                        createNewEvents = createNewEvents.replace(u'{deleted}', deletedFlag)
                        createNewDiagnostic = createNewDiagnostic.replace(u'{deleted}', deletedFlag)
                        createNewDiagnosis = createNewDiagnosis.replace(u'{deleted}', deletedFlag)
                        visitPersonId = forceString(x.value('visitPersonId'))
                        eventId = forceString(x.value('event_id'))
                        diagnosisId = forceString(x.value('diagnosis_id'))
                        diagnosticId = forceString(x.value('diagnostic_id'))
                        visitId = forceString(x.value('visit_id'))

                        # this need for search id
                        eventCond = 'VM_TEST_QUERY. Old `event_id` = %s' % eventId + '; `visit_id` IN (%s)' % visitId

                        createNewEvents = createNewEvents.replace(u'{visitQueryList}', forceString(visitId))
                        createNewEvents = createNewEvents.replace(u'{eventCond}', eventCond)
                        queryEvent = db.query(
                            createNewEvents % (
                                visitPersonId,
                                eventId,
                                visitId
                            )
                        )
                        # this need for search id
                        # eventCond = 'VM_TEST_QUERY. Old `event_id` = %s' % eventId + '; `visit_id` IN (%s)' % visitId

                        createNewDiagnosis = createNewDiagnosis.replace(u'{eventCond}', eventCond)
                        queryDiagnosis = db.query(
                            createNewDiagnosis % (
                                visitPersonId,
                                diagnosisId
                            )
                        )
                        queryDiagnosis.next()
                        diagnosisRecord = db.getRecordEx(
                            table='Diagnosis',
                            cols='id',
                            where=[
                                'note LIKE \'%s%%\'' % eventCond,
                                'deleted = 0'
                            ]
                        )
                        if diagnosisRecord:
                            lastDiagnosisId = forceString(diagnosisRecord.value('id'))
                        else:
                            print u'Event.id = %s | Не найден новый диагноз, возможно эвент удален.' % eventId
                            continue

                        queryEvent.next()
                        eventRecord = db.getRecordEx(
                            table='Event',
                            cols='id',
                            where=[
                                'note LIKE \'%s%%\'' % eventCond,
                                'deleted = 0'
                            ]
                        )
                        if eventRecord:
                            lastEventId = forceString(eventRecord.value('id'))
                        else:
                            print u'Event.id = %s | Не найден новый эвент, возможно старый эвент удален.' % eventId
                            continue

                        createNewDiagnostic = createNewDiagnostic.replace(u'{eventCond}', eventCond)
                        queryDiagnostic = db.query(
                            createNewDiagnostic % (
                                lastEventId,
                                lastDiagnosisId,
                                visitPersonId,
                                diagnosticId
                            )
                        )

                        queryDiagnostic.next()
                        diagnosticRecord = db.getRecordEx(
                            table='Diagnostic',
                            cols='id',
                            where=[
                                'notes LIKE \'%s%%\'' % eventCond,
                                'deleted = 0'
                            ]
                        )
                        if diagnosticRecord:
                            lastDiagnosticId = forceString(diagnosticRecord.value('id'))
                        else:
                            print u'Event.id = %s | Не найден новый Diagnostic, возможно эвент удален.' % eventId
                            continue

                        eventsList.append(
                            {
                                'event_id': eventId,
                                'diagnostic_id': diagnosticId,
                                'diagnosis_id': diagnosisId,
                                'visit_id': visitId,
                                'visitPersonId': visitPersonId,
                                'newEvent_id': lastEventId,
                                'newDiagnosis_id': lastDiagnosisId,
                                'newDiagnostic_id': lastDiagnosticId,
                            }
                        )
                    except Exception as e:
                        print e

                for x in eventsList:
                    try:
                        if x['visit_id']:
                            cond = ['id = %s' % x['visit_id']]
                            visit = db.getRecordList(table='Visit', cols='*', where=cond)
                            if visit:
                                for y in visit:
                                    y.setValue('event_id', toVariant(x['newEvent_id']))
                                    y.setValue('payStatus', toVariant(0))
                                    db.insertOrUpdate('Visit', y)
                            else:
                                print u'Event.id = %s | Не найдены посещения, возможно эвент удален.' % x['event_id']
                                continue

                            cond = ['id = %s' % x['event_id']]
                            event = db.getRecordEx(table='Event', cols='*', where=cond)
                            if event:
                                note = 'Create VM_TEST_QUERY. Old `visit_id` = %s\n' % x['visit_id']
                                event.setValue('note', toVariant(note + forceString(event.value('note'))))
                                db.insertOrUpdate('Event', event)
                            else:
                                print u'Event.id = %s | Не найден старый эвент, возможно он удален.' % x['event_id']
                                continue
                    except Exception as e:
                        print e

                rm = db.query(removeEmptyEvents)
                rm.next()

                # QtGui.QMessageBox.information(
                #     self,
                #     u'Перевыставление обращении Event 2',
                #     u'Перевыставление завершено успешно.',
                #     QtGui.QMessageBox.Ok
                # )
            else:
                QtGui.QMessageBox.information(
                    self,
                    u'Перевыставление обращении Event 2',
                    u'Нет данных для перевыставления.',
                    QtGui.QMessageBox.Ok
                )
            print u'Block 2'
        except Exception as e:
            QtGui.QMessageBox.critical(
                self,
                u'Перевыставление обращении Event 2',
                u'Не удалось выполнить перевыставление: "%s"' % e,
                QtGui.QMessageBox.Close
            )

    def recreateEvent_3(self):
        eventsList = []
        db = QtGui.qApp.db

        deletedFlag = '1' if self.chkDebug.isChecked() else '0'
        mesIdTerap = forceString(self.edtEvent3MesIdTerap.value()) if self.edtEvent3MesIdTerap.value() else u'NULL'
        mesIdVop = forceString(self.edtEvent3MesIdVop.value()) if self.edtEvent3MesIdVop.value() else u'NULL'
        mesIdPed = forceString(self.edtEvent3MesIdPed.value()) if self.edtEvent3MesIdPed.value() else u'NULL'

        oldEventsQuery = u"""
            SELECT DISTINCT
                e.id AS event_id,
                d.id AS diagnostic_id,
                d1.id AS diagnosis_id,
                v.id AS visit_id,
                v.person_id AS visitPersonId
            FROM
                Event e
                INNER JOIN Visit v ON e.id = v.event_id AND v.deleted = 0
                INNER JOIN Person p ON v.person_id = p.id
                INNER JOIN rbSpeciality s ON p.speciality_id = s.id
                INNER JOIN OrgStructure os ON p.orgStructure_id = os.id AND os.isArea <> 0
                INNER JOIN Diagnostic d ON d.event_id = e.id AND d.deleted = 0
                INNER JOIN Diagnosis d1 ON d.diagnosis_id = d1.id AND d.deleted = 0
            WHERE
                e.deleted = 0
                AND d.diagnosisType_id IN (1, 2)
                AND e.execDate >= '{begDate}' AND e.execDate <= '{endDate}'
                AND date(v.date) >= '2017-01-01'
                # AND e.execDate >= '2017-01-09' AND e.execDate <= '2017-01-11'
                AND e.eventType_id IN ({eventType})
                AND e.contract_id IN ({contractId})
                # AND e.eventType_id IN (50)
                # AND e.contract_id IN (69)
                AND v.scene_id NOT IN (2, 3)
                AND (s.name LIKE 'Терапевт%%' OR s.name LIKE 'ВОП%%' OR s.name LIKE 'Врач ОП%%' OR s.name LIKE 'Педиатр%%')
                AND e.note NOT LIKE 'VM_TEST_QUERY%%'
                AND EXISTS
                (
                    # SELECT DISTINCT
                    #   v1.event_id AS event_id,
                    #   COUNT(v1.id)
                    # FROM
                    #   Visit v1
                    # WHERE
                    #   e.id = v1.event_id AND v1.deleted = 0
                    #   AND v.person_id = v1.person_id
                    # GROUP BY v1.event_id
                    # HAVING COUNT(v1.id) > 1
                    SELECT DISTINCT
                      v1.event_id AS event_id,
                      v1.person_id,
                      COUNT(v1.id)
                    FROM
                      Visit v1
                    WHERE
                      v1.deleted = 0
                      AND v1.event_id = e.id
                      AND v.person_id = v1.person_id
                    GROUP BY v1.person_id
                    HAVING COUNT(v1.id) > 1
                )
                # AND e.id = 2061411
            """
        oldEventsQuery = oldEventsQuery.replace(u'{begDate}', self.edtSetDateFrom.date().toString('yyyy-MM-dd'))
        oldEventsQuery = oldEventsQuery.replace(u'{endDate}', self.edtSetDateTo.date().toString('yyyy-MM-dd'))
        oldEventsQuery = oldEventsQuery.replace(u'{eventType}', self.edtEventItem.text())
        oldEventsQuery = oldEventsQuery.replace(u'{contractId}', self.edtContractsId.text())

        try:
            records = db.getRecordList(stmt=oldEventsQuery)
            if records:
                for x in records:
                    visitPersonId = forceString(x.value('visitPersonId'))
                    eventId = forceString(x.value('event_id'))
                    diagnosisId = forceString(x.value('diagnosis_id'))
                    diagnosticId = forceString(x.value('diagnostic_id'))
                    visitId = forceString(x.value('visit_id'))

                    isAppended = False
                    for y in eventsList:
                        if y['event_id'] == eventId and y['diagnostic_id'] == diagnosticId \
                                and y['diagnosis_id'] == diagnosisId and visitId not in y['visitList']:
                            isAppended = True
                            y['visitList'].append(visitId)
                            y['visitQueryList'] += ', %s' % visitId
                            break

                    if not isAppended:
                        event = dict([
                            ('event_id', eventId),
                            ('diagnostic_id', diagnosticId),
                            ('diagnosis_id', diagnosisId),
                            ('visitList', [visitId]),
                            ('visitQueryList', visitId),
                            ('visitPersonId', visitPersonId),
                            ('newEvent_id', 0),
                            ('newDiagnosis_id', 0),
                            ('newDiagnostic_id', 0)
                        ])
                        eventsList.append(event)

                for event in eventsList:
                    createNewEvents = u"""
                        INSERT INTO Event (
                          createDatetime,
                          createPerson_id,
                          eventType_id, -- here
                          org_id,
                          client_id,
                          setDate,
                          setPerson_id,
                          execDate,
                          execPerson_id,
                          isPrimary,
                          `order`,
                          result_id,
                          payStatus,
                          pregnancyWeek,
                          MES_id,
                          totalCost,
                          goal_id,
                          clientPolicy_id,
                          deleted,
                          note,
                          contract_id
                        )
                        # VALUES
                          SELECT DISTINCT
                            CURRENT_TIMESTAMP,
                            e.createPerson_id,
                            {newEventType}, #176, # 105, # 176, # e1.eventType_id,
                            e.org_id,
                            e.client_id,
                            IF(e.setDate < '2017-01-01', '2017-01-01', e.setDate), # e.setDate,
                            e.setPerson_id,
                            e.execDate,
                            %s, # e.execPerson_id,
                            e.isPrimary,
                            e.`order`,
                            {result_id}, # e.result_id,
                            0, # e.payStatus,
                            e.pregnancyWeek,
                            # IF(s.name LIKE 'Терапевт', 2080, IF(s.name LIKE 'ВОП%%', 2074, NULL)) AS MES_id, # e1.MES_id,
                            IF(s.name LIKE 'Терапевт', {MES_id_terap}, IF(s.name LIKE 'ВОП%%' OR s.name LIKE 'Врач ОП%%', {MES_id_vop}, IF(s.name LIKE 'Педиатр%%', {MES_id_ped}, NULL))) AS MES_id, # e1.MES_id,
                            e.totalCost,
                            {goal_id}, # e.goal_id,
                            e.clientPolicy_id,
                            {deleted},
                            # concat('VM_TEST_QUERY. Old `event_id` = ', e.id),
                            '{eventCond}', # concat('VM_TEST_QUERY. Old `event_id` = ', e.id, '; `visit_id` IN ({visitQueryList})'),
                            {newContractId}
                          FROM
                            EVENT e
                            INNER JOIN Visit v ON e.id = v.event_id AND v.deleted = 0
                            INNER JOIN Person p ON v.person_id = p.id
                            INNER JOIN rbSpeciality s ON p.speciality_id = s.id
                            INNER JOIN OrgStructure os ON p.orgStructure_id = os.id AND os.isArea <> 0
                          WHERE
                            e.id = %s
                            AND v.id IN (%s)
                          LIMIT 1
                        """
                    createNewDiagnostic = u"""
                        INSERT INTO Diagnostic (
                          createDatetime,

                          createPerson_id,
                          event_id, -- HERE
                          diagnosis_id, -- HERE
                          diagnosisType_id,
                          setDate,
                          endDate,
                          character_id,
                          stage_id,
                          dispanser_id,
                          sanatorium,
                          hospital,
                          speciality_id,
                          person_id,
                          healthGroup_id,
                          result_id,
                          deleted,
                          notes
                        )
                        # VALUES
                          SELECT DISTINCT
                            CURRENT_TIMESTAMP,
                            createPerson_id,
                            %s, # event_id, -- HERE
                            %s, # diagnosis_id, -- HERE
                            diagnosisType_id,
                            setDate,
                            endDate,
                            character_id,
                            stage_id,
                            dispanser_id,
                            sanatorium,
                            hospital,
                            speciality_id,
                            %s, # person_id,
                            healthGroup_id,
                            {result_id},
                            {deleted},
                            '{eventCond}' # concat('VM_TEST_QUERY. Old `diagnostic_id` = ', d.id)
                          FROM
                            Diagnostic d
                          WHERE
                            d.id = %s
                          LIMIT 1
                        """
                    createNewDiagnosis = u"""
                        INSERT INTO Diagnosis (
                          createDatetime,
                          modifyDatetime,
                          createPerson_id,
                          deleted,
                          client_id,
                          diagnosisType_id,
                          character_id,
                          MKB,
                          MKBEx,
                          morphologyMKB,
                          TNMS,
                          dispanser_id,
                          traumaType_id,
                          setDate,
                          endDate,
                          mod_id,
                          person_id,
                          tempEventId,
                          note
                        )
                       SELECT
                          CURRENT_TIMESTAMP,
                          CURRENT_TIMESTAMP,
                          createPerson_id,
                          {deleted},
                          client_id,
                          diagnosisType_id,
                          character_id,
                          MKB,
                          MKBEx,
                          morphologyMKB,
                          TNMS,
                          dispanser_id,
                          traumaType_id,
                          setDate,
                          endDate,
                          mod_id,
                          %s, # person_id,
                          tempEventId,
                          '{eventCond}'
                        FROM Diagnosis d WHERE d.id = %s
                        LIMIT 1
                        """
                    removeEmptyEvents = u"""
                        UPDATE
                          Event e
                        SET
                          e.deleted = 1
                        WHERE
                          e.deleted = 0
                          AND (e.note LIKE 'Create VM%' OR e.note LIKE 'VM_TEST%')
                          AND EXISTS
                          (
                            SELECT DISTINCT
                              v1.event_id AS event_id,
                              COUNT(v1.id)
                            FROM
                              Visit v1
                            WHERE
                              e.id = v1.event_id AND v1.deleted = 0
                            GROUP BY v1.event_id
                            HAVING COUNT(v1.id) = 0
                          )
                        """

                    createNewEvents = createNewEvents.replace(u'{newEventType}',
                                                              forceString(self.edtEvent3TypeId.value()))
                    createNewEvents = createNewEvents.replace(u'{newContractId}',
                                                              forceString(self.edtEvent3ContractId.value()))
                    createNewEvents = createNewEvents.replace(u'{result_id}',
                                                              forceString(self.edtEvent3ResultId.value()))
                    createNewEvents = createNewEvents.replace(u'{goal_id}', forceString(self.edtEvent3GoalId.value()))
                    createNewEvents = createNewEvents.replace(u'{MES_id_terap}', mesIdTerap)
                    createNewEvents = createNewEvents.replace(u'{MES_id_vop}', mesIdVop)
                    createNewEvents = createNewEvents.replace(u'{MES_id_ped}', mesIdPed)

                    createNewDiagnostic = createNewDiagnostic.replace(u'{result_id}', forceString(
                        self.edtEvent3DiagnosticResultId.value()))

                    createNewEvents = createNewEvents.replace(u'{deleted}', deletedFlag)
                    createNewDiagnostic = createNewDiagnostic.replace(u'{deleted}', deletedFlag)
                    createNewDiagnosis = createNewDiagnosis.replace(u'{deleted}', deletedFlag)

                    visitPersonId = event['visitPersonId']
                    eventId = event['event_id']
                    diagnosisId = event['diagnosis_id']
                    diagnosticId = event['diagnostic_id']
                    visitId = event['visitQueryList']

                    # this need for search id
                    eventCond = 'VM_TEST_QUERY. Old `event_id` = %s' % event['event_id'] + '; `visit_id` IN (%s)' % \
                                                                                           event[
                                                                                               'visitQueryList'] + 'personId = %s' % \
                                                                                                                   event[
                                                                                                                       'visitPersonId']

                    createNewEvents = createNewEvents.replace(u'{visitQueryList}', forceString(visitId))
                    createNewEvents = createNewEvents.replace(u'{eventCond}', eventCond)
                    queryEvent = db.query(
                        createNewEvents % (
                            visitPersonId,
                            eventId,
                            visitId
                        )
                    )
                    # this need for search id
                    # eventCond = 'VM_TEST_QUERY. Old `event_id` = %s' % eventId + '; `visit_id` IN (%s)' % visitId

                    createNewDiagnosis = createNewDiagnosis.replace(u'{eventCond}', eventCond)
                    queryDiagnosis = db.query(
                        createNewDiagnosis % (
                            visitPersonId,
                            diagnosisId
                        )
                    )

                    queryDiagnosis.next()
                    diagnosisRecord = db.getRecordEx(
                        table='Diagnosis',
                        cols='id',
                        where=[
                            'note LIKE \'%s%%\'' % eventCond,
                            'deleted = 0'
                        ]
                    )
                    if diagnosisRecord:
                        lastDiagnosisId = forceString(diagnosisRecord.value('id'))
                    else:
                        print u'Event.id = %s | Не найден новый диагноз, возможно эвент удален.' % eventId
                        eventsList.remove(event)
                        continue

                    queryEvent.next()
                    eventRecord = db.getRecordEx(
                        table='Event',
                        cols='id',
                        where=[
                            'note LIKE \'%s%%\'' % eventCond,
                            'deleted = 0'
                        ]
                    )
                    if eventRecord:
                        lastEventId = forceString(eventRecord.value('id'))
                    else:
                        print u'Event.id = %s | Не найден новый эвент, возможно старый эвент удален.' % eventId
                        eventsList.remove(event)
                        continue

                    createNewDiagnostic = createNewDiagnostic.replace(u'{eventCond}', eventCond)
                    queryDiagnostic = db.query(
                        createNewDiagnostic % (
                            lastEventId,
                            lastDiagnosisId,
                            visitPersonId,
                            diagnosticId
                        )
                    )

                    queryDiagnostic.next()
                    diagnosticRecord = db.getRecordEx(
                        table='Diagnostic',
                        cols='id',
                        where=[
                            'notes LIKE \'%s%%\'' % eventCond,
                            'deleted = 0'
                        ]
                    )
                    if diagnosticRecord:
                        lastDiagnosticId = forceString(diagnosticRecord.value('id'))
                    else:
                        print u'Event.id = %s | Не найден новый Diagnostic, возможно эвент удален.' % eventId
                        eventsList.remove(event)
                        continue

                    event['newEvent_id'] = lastEventId
                    event['newDiagnosis_id'] = lastDiagnosisId
                    event['newDiagnostic_id'] = lastDiagnosticId

                for x in eventsList:
                    if x['visitQueryList']:
                        cond = ['id IN (%s)' % x['visitQueryList']]
                        visit = db.getRecordList(table='Visit', cols='*', where=cond)
                        if visit:
                            for y in visit:
                                y.setValue('event_id', toVariant(x['newEvent_id']))
                                y.setValue('payStatus', toVariant(0))
                                db.insertOrUpdate('Visit', y)
                        else:
                            print u'Event.id = %s | Не найдены посещения, возможно эвент удален.' % x['event_id']
                            continue

                        cond = ['id = %s' % x['event_id']]
                        event = db.getRecordEx(table='Event', cols='*', where=cond)
                        if event:
                            note = 'Create VM_TEST_QUERY. Old `visit_id` IN (%s)\n' % x['visitQueryList']
                            event.setValue('note', toVariant(note + forceString(event.value('note'))))
                            db.insertOrUpdate('Event', event)
                        else:
                            print u'Event.id = %s | Не найден старый эвент, возможно он удален.' % x['event_id']
                            continue

                rm = db.query(removeEmptyEvents)
                rm.next()

                # QtGui.QMessageBox.information(
                #     self,
                #     u'Перевыставление обращении Event 3',
                #     u'Перевыставление завершено успешно.',
                #     QtGui.QMessageBox.Ok
                # )
            else:
                QtGui.QMessageBox.information(
                    self,
                    u'Перевыставление обращении Event 3',
                    u'Нет данных для перевыставления.',
                    QtGui.QMessageBox.Ok
                )
            print u'Block 3'
        except Exception as e:
            QtGui.QMessageBox.critical(
                self,
                u'Перевыставление обращении Event 3',
                u'Не удалось выполнить перевыставление: "%s"' % e,
                QtGui.QMessageBox.Close
            )

    def accept(self):
        try:
            if self.Event1.isChecked():
                self.recreateEvent_1()
            if self.Event2.isChecked():
                self.recreateEvent_2()
            if self.Event3.isChecked():
                self.recreateEvent_3()
        except Exception as e:
            QtGui.QMessageBox.critical(
                self,
                u'Перевыставление обращении',
                u'Не удалось выполнить перевыставление: "%s"' % e,
                QtGui.QMessageBox.Close
            )

def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    connectionInfo = {
        'driverName': 'mysql',
        'host': '192.168.0.3',
        'port': 3306,
        'database': 'dkkb_test',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)


    form = CRecreateDialog()
    form.show()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()
