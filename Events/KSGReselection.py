# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Events.Ui_KSGReselectionDialog import Ui_KSGReselectionDialogForm
from library.CSG.Utils import getCsgIdListByCond, getCSGDepartmentMaskByRegionalCode
from library.Utils import calcAgeTuple, forceDate, forceRef, forceInt, forceString


class CKSGReselection(QtGui.QDialog, Ui_KSGReselectionDialogForm):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.badEvents = []
        self.ambiguousEvents = []

    @QtCore.pyqtSlot()
    def on_btnStart_clicked(self):
        self.badEvents = []
        self.ambiguousEvents = []
        self.processEvents(self.begDate.date(), self.endDate.date())

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    def processEvents(self, startDate, endDate):
        db = QtGui.qApp.db
        self.btnStart.setEnabled(False)
        self.logBrowser.append(u'Перевыставление начато')

        getEventsStmt = u'''
          SELECT
              Event.id                                              as eventId,
              EP.regionalCode                                       as eventCode,
              Client.sex                                            as sex,
              Client.birthDate                                      as bDay,
              Event.setDate                                         as setDate,
              Event.execDate                                        as execDate
          FROM
              Event
              INNER JOIN EventType ON Event.eventType_id = EventType.id
              INNER JOIN rbEventProfile AS EP ON EventType.eventProfile_id = EP.id
              INNER JOIN Client ON Event.client_id = Client.id
          WHERE(
              EP.regionalCode = '11' OR EP.regionalCode = '12' OR EP.regionalCode = '51' OR EP.regionalCode = '52' OR
              EP.regionalCode = '71' OR EP.regionalCode = '72' OR EP.regionalCode = '41' OR EP.regionalCode = '42' OR
              EP.regionalCode = '90' OR EP.regionalCode = '43') AND
              Event.execDate BETWEEN '%s' AND '%s'
              AND Event.deleted = 0 AND Client.deleted = 0
        ''' % (startDate.toString('yyyy.MM.dd'), endDate.toString('yyyy.MM.dd'))
        eventsQ = db.query(getEventsStmt)
        events = []
        while eventsQ.next():
            QtGui.qApp.processEvents()
            record = eventsQ.record()

            event = {}
            event['id'] = forceRef(record.value('eventId'))
            event['sex'] = forceInt(record.value('sex'))
            event['age'] = calcAgeTuple(forceDate(record.value('bDay')), forceDate(record.value('setDate')))

            event['code'] = getCSGDepartmentMaskByRegionalCode(forceString(record.value('eventCode')))
            event['setDate'] = forceDate(record.value('setDate'))
            event['execDate'] = forceDate(record.value('execDate'))

            getMKBstmt = u'''
                SELECT Diagnosis.MKB
                FROM Event INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
                WHERE Event.id = '%i' AND (rbDiagnosisType.name = 'заключительный' OR rbDiagnosisType.name = 'основной')
                LIMIT 1
            ''' % (event['id'])
            mkbQ = db.query(getMKBstmt)
            mkbQ.next()
            mkbQ = mkbQ.record()
            if not mkbQ:
                self.badEvents.append(event['id'])
                continue
            mkb = forceString(mkbQ.value('MKB'))
            event['mkb'] = mkb

            getMKB2stmt = u'''
                SELECT Diagnosis.MKB
                FROM Event INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
                WHERE Event.id = '%i' AND rbDiagnosisType.name = 'сопутствующий'
            ''' % (event['id'])
            mkbQ = db.query(getMKB2stmt)
            mkb2 = []
            while mkbQ.next():
                mkb2.append(forceString(mkbQ.record().value('MKB')))
            event['mkb2'] = mkb2

            getActionCodesstmt = u'''
                SELECT ActionType.code
                FROM Event INNER JOIN Action ON Event.id = Action.event_id INNER JOIN ActionType ON Action.actionType_id = ActionType.id
                WHERE Event.id = '%i' AND Action.status = 2 AND Action.deleted = 0
            ''' % (event['id'])
            actQ = db.query(getActionCodesstmt)
            actCodes = []
            while actQ.next():
                actCodes.append(forceString(actQ.record().value('code')))
            event['ATCodes'] = actCodes

            events.append(event)

        self.logBrowser.append(u'Список случаев получен: %i' % len(events))
        self.reselectKSG(events)

    def reselectKSG(self, events):
        db = QtGui.qApp.db
        tblEvent = db.table('Event')
        self.progressBar.setMaximum(len(events))
        i = 0
        for event in events:
            i+=1; self.progressBar.setValue(i)
            QtGui.qApp.processEvents()
            SPR69Ids = getCsgIdListByCond(sex=event['sex'], age=event['age'], mkb=event['mkb'], mkb2List=event['mkb2'], actionTypeCodesList=event['ATCodes'], code=event['code'], date=event['execDate'], duration=event['setDate'].daysTo(event['execDate']))
            if not SPR69Ids:
                self.badEvents.append(event['id'])
                continue
            elif len(SPR69Ids) > 1:
                self.ambiguousEvents.append(event['id'])
                query = db.query(u'''SELECT id FROM mes.SPR69 WHERE id in (%s) ORDER BY KSGKoeff DESC LIMIT 1''' % str(SPR69Ids).strip(u'[]'))
                query.first()
                SPR69Id = forceRef(query.value(0))
            else:
                SPR69Id = SPR69Ids[0]

            eventRecord = db.getRecordEx(tblEvent, 'id, MES_id', [tblEvent['id'].eq(event['id'])])
            tblSPR69 = db.table('mes.SPR69')
            tblMES = db.table('mes.MES')
            table = tblSPR69.innerJoin(tblMES, db.joinAnd([
                tblMES['code'].eq(tblSPR69['KSG']),
                tblMES['begDate'].le(tblSPR69['endDate']),
                tblMES['endDate'].ge(tblSPR69['begDate'])
            ]))
            record = db.getRecordEx(table, 'MES.id', [tblSPR69['id'].eq(SPR69Id), tblMES['deleted'].eq(0)])
            mesId = forceRef(record.value('id'))
            if not mesId:
                self.badEvents.append(event['id'])
            else:
                # eventRecord.setValue('MES_id', QtCore.QVariant(mesId))
                eventRecord.setValue('KSG_id', QtCore.QVariant(mesId))
                db.updateRecord(tblEvent, eventRecord)

        self.logBrowser.append(u'Перевыставление закончено!')
        self.logBrowser.append(u'Перевыставлено %i обращений' % (i - len(self.badEvents)))
        if self.badEvents:
            self.logBrowser.append(u'Данные случаи перевыставить не удалось: {eventId}')
            self.logBrowser.append(str(self.badEvents))
        if self.ambiguousEvents:
            self.logBrowser.append(u'В данных случаях была неоднозначность: {eventId}')
            self.logBrowser.append(str(self.ambiguousEvents))
        self.btnStart.setEnabled(True)

