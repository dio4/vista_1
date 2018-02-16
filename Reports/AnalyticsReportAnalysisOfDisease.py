# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceInt, forceString
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportAnalysisOfDisease import Ui_ReportAnalysisOfDisease


def selectData(params):
    begDate                 = params.get('begDate', None)
    endDate                 = params.get('endDate', None)
    eventTypeId             = params.get('eventTypeId', None)
    finishedDiagnosis       = params.get('finishedDiagnosis', None)

    db = QtGui.qApp.db

    tableEvent                      = db.table('Event')
    tableResult                     = db.table('rbResult')
    tableActionType                 = db.table('ActionType')
    tableOrgStructure               = db.table('OrgStructure')
    tableActionProperty             = db.table('ActionProperty')
    tableAPString                   = db.table('ActionProperty_String')
    tableAPOrgStructure             = db.table('ActionProperty_OrgStructure')
    tableAction                     = db.table('Action')
    tableAct                        = db.table('Action').alias('act')
    tableActProperty                = db.table('ActionProperty').alias('actProperty')
    tableActPropertyType            = db.table('ActionPropertyType').alias('actPropertyType')
    tableDiagnostic                 = db.table('Diagnostic')
    tableDiagnosis                  = db.table('Diagnosis')
    tableDiagnosisType              = db.table('rbDiagnosisType')

    queryTable = tableEvent.innerJoin(tableAction, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionProperty, tableAction['id'].eq(tableActionProperty['action_id']))
    queryTable = queryTable.leftJoin(tableAPString, tableActionProperty['id'].eq(tableAPString['id']))
    queryTable = queryTable.innerJoin(tableAct, '''act.event_id AND act.id = (SELECT max(a.id)
                                                                                 FROM Action a
                                                                                      INNER JOIN ActionType aType
                                                                                            ON aType.id = a.actionType_id AND aType.flatCode = 'moving'
                                                                                      WHERE a.deleted = 0 AND
                                                                                            Action.event_id = a.event_id)''')
    queryTable = queryTable.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    queryTable = queryTable.innerJoin(tableActProperty, tableAct['id'].eq(tableActProperty['action_id']))
    queryTable = queryTable.innerJoin(tableActPropertyType, tableActPropertyType['id'].eq(tableActProperty['type_id']))
    queryTable = queryTable.innerJoin(tableAPOrgStructure, tableAPOrgStructure['id'].eq(tableActProperty['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableAPOrgStructure['value']))
    if finishedDiagnosis:
        queryTable = queryTable.innerJoin(tableDiagnostic, tableDiagnostic['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
        queryTable = queryTable.innerJoin(tableDiagnosisType, [tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']),
                                                               tableDiagnosisType['code'].inlist(['1', '2'])])

    cols = [tableOrgStructure['name'],
            u'''count(DISTINCT Event.id) AS everybody,
                group_concat(DISTINCT Event.externalId) AS everybodeExternatId,
                count(DISTINCT if(ActionProperty_String.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '12-24 часов', '7-24 часов'), Event.id,NULL)) AS receivedBeforDay,
                count(DISTINCT if(ActionProperty_String.value IN('более 24-х часов',  'менее 2 суток', 'менее 3 суток', 'менее 4 суток', 'менее 5 суток', 'менее 6 суток', 'менее 7 суток', 'более 7 суток'), Event.id,NULL)) AS receivedAfterDay,
                count(DISTINCT if((rbResult.code = '105' or rbResult.code = '106')  and DATE(Event.execDate) = DATE(Event.setDate), Event.id, NULL)) AS deadBeforDay,
                count(DISTINCT if((rbResult.code = '105' or rbResult.code = '106') and DATE(Event.execDate) > DATE(Event.setDate), Event.id, NULL)) AS deadAfterDay,
                count(DISTINCT if((rbResult.code = '105' or rbResult.code = '106'), Event.id,NULL)) AS dead,
                group_concat(DISTINCT if((rbResult.code = '105' OR rbResult.code = '106'), Event.externalId, NULL)) AS deadExternatId''']
    cond = [tableEvent['execDate'].dateLe(endDate),
            tableEvent['execDate'].dateGe(begDate),
            tableEvent['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableAct['deleted'].eq(0),
            tableOrgStructure['deleted'].eq(0),
            tableActionType['flatCode'].eq('received'),
            tableActPropertyType['name'].like(u'Отделение пребывания%'),
            db.joinOr([tableDiagnosis['MKB'].like('I21%'), tableDiagnosis['MKB'].like('I22%'), tableDiagnosis['MKB'].like('I23%')]) if finishedDiagnosis else u'''(act.`MKB` LIKE 'I21%') OR (act.MKB LIKE 'I22%') OR (act.MKB LIKE 'I23%')''']
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    stmt = db.selectStmt(queryTable, cols, cond, group=tableOrgStructure['name'])
    return db.query(stmt)


class CAnalyticsReportAnalysisOfDisease(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Анализ заболеваний "Острый инфаркт миокарда"')

    def getSetupDialog(self, parent):
        result = CStationaryAnalyticsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        orgGroup = params.get('orgGroup', True)
        tableColumns = [
            ('2%',  [u'№'                                          ], CReportBase.AlignLeft),
            ('25%', [u'Подразделение'                              ], CReportBase.AlignLeft),
            ( '15%', [u'Количество больных'                         ], CReportBase.AlignCenter),
            ('15%', [u'№ИБ'                         ], CReportBase.AlignCenter),
            ( '10%', [u'Доставлено от начала заболевания через', u'до суток'], CReportBase.AlignRight),
            ( '10%', [u'',                                       u'позднее суток'], CReportBase.AlignRight),
            ( '10%', [u'Умерло',                                 u'Всего'], CReportBase.AlignRight),
            ('15%', [u'',                                        u'№ИБ'                         ], CReportBase.AlignCenter),
            ( '10%', [u'',                                       u'Летал.'], CReportBase.AlignRight),
            ( '10%', [u'',                                       u'до суток'], CReportBase.AlignRight),
            ( '10%', [u'',                                       u'позднее суток'], CReportBase.AlignRight),]
        if not orgGroup:
            tableColumns = tableColumns[:3] + tableColumns[4:7] + tableColumns[8:]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        if orgGroup:
            table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4 if orgGroup else 3, 1, 2)
        table.mergeCells(0, 6 if orgGroup else 5, 1, 5 if orgGroup else 4)
        total = [0]*(len(tableColumns) - 2)

        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()

            dead = forceInt(record.value('dead'))
            countClient = forceInt(record.value('everybody'))
            fields = (
                forceString(record.value('name')),
                countClient,
                forceString(record.value('everybodeExternatId')).replace(',', '\n'),
                forceInt(record.value('receivedBeforDay')),
                forceInt(record.value('receivedAfterDay')),
                dead,
                forceString(record.value('deadExternatId')).replace(',', '\n'),
                dead*100/countClient,
                forceInt(record.value('deadBeforDay')),
                forceInt(record.value('deadAfterDay'))
            )
            if not orgGroup:
                fields = fields[:2] + fields[3:6] + fields[7:]
            i = table.addRow()
            table.setText(i, 0, i-1)
            for col, val in enumerate(fields):
                table.setText(i, col + 1, val if val else '')
                if col and isinstance(val, int):
                    total[col - 1] += val

        i = table.addRow()
        table.setText(i, 1, u'Всего', CReportBase.TableTotal)
        for index, val in enumerate(total):
            if val:
                if not orgGroup and index != 4 or orgGroup and index != 6:
                    table.setText(i, index + 2, val, CReportBase.TableTotal)
                elif total[3 if not orgGroup else 4]:
                    table.setText(i, index + 2, total[3 if not orgGroup else 4]*100/total[0], CReportBase.TableTotal)
        return doc

class CStationaryAnalyticsSetupDialog(QtGui.QDialog, Ui_ReportAnalysisOfDisease):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.chkFinishedDiagnosis.setChecked(params.get('finishedDiagnosis', False))
        self.chkOrgGroup.setChecked(params.get('orgGroup', True))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['eventTypeId'] = self.cmbEventType.value()
        params['finishedDiagnosis'] = self.chkFinishedDiagnosis.isChecked()
        params['orgGroup'] = self.chkOrgGroup.isChecked()
        return params