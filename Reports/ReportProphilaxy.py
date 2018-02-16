# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from library.Utils      import *
from Reports.Report      import CReport
from Reports.ReportBase import *
from ReportPrimaryRepeatHospitalization import CPrimaryRepeatHospitalization

diagnosis = [u'T01.8', u'S01.0', u'S01.1', u'S01.2', u'S01.3', u'S01.4', u'S01.5', u'S01.7', u'S01.8', u'S01.9',
             u'S11.8', u'S21.0', u'S21.1', u'S21.2', u'S21.7', u'S21.8', u'S21.9', u'S31.0', u'S31.1', u'S31.2',
             u'S31.3', u'S71.0', u'S71.1', u'S81.0', u'S81.7', u'S81.8', u'S91.0', u'S91.1', u'S91.3', u'S41.0',
             u'S41.1', u'S41.7', u'S51.0', u'S51.7', u'S51.8', u'S61.0', u'S61.8', u'S67.0', u'S67.8', u'S68.0',
             u'S68.1', u'S68', u'T33']

def selectData(begDate, endDate, isEventCreateParams, eventBegDatetime, eventEndDatetime, eventTypeId):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableDiagnosis = db.table('Diagnosis')

    cond = []

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if isEventCreateParams:
        cond.append(tableDiagnosis['createDatetime'].dateGe(eventBegDatetime))
        cond.append(tableDiagnosis['createDatetime'].dateLe(eventEndDatetime))
    else:
        cond.append(tableDiagnosis['setDate'].dateGe(begDate))
        cond.append(tableDiagnosis['setDate'].dateLe(endDate))

    stmt = u'''SELECT age(Client.birthDate, Diagnosis.setDate) AS ageClient
                 , count(Diagnosis.id) AS cnt
                 , count(if(Client.id = 1, Diagnosis.id, NULL)) AS cntMen
                 , count(Event.id) AS cntEvent
                 , count(if(ActionProperty_String.value LIKE "%%АДСМ%%", Event.id, NULL)) AS cntADCM
                 , count(if(ActionProperty_String.value = '0.5 АС+0.5 АДСМ+ПСС', Event.id, NULL)) AS cntAC_ADCM_PCC
                 , count(if(ActionProperty_String.value = '1.0 АС + 0.5 АДМ + ПСС', Event.id, NULL)) AS cntAC_ADM_PCC
                 , count(if(ActionProperty_String.value = '1.0 АС + ПСС', Event.id, NULL)) AS cntAC_PCC
                 , count(if(ActionProperty_String.value = '0.5 АС + 0.5 АДСМ', Event.id, NULL)) AS cntAC_ADMC
                 , count(if(ActionProperty_String.value = '1.0 АС + 0.5 АДМ', Event.id, NULL)) AS cntAC_ADM
                 , count(if(ActionProperty_String.value = '1.0 АС', Event.id, NULL)) AS cntAC
                 , count(if(ActionProperty_String.value = 'Ревакцинация 0.5 АДСМ', Event.id, NULL)) AS cntReADCM
                 , count(if(ActionProperty_String.value = 'Ревакцинация 0.5 АС', Event.id, NULL)) AS cntReAC
               FROM
                Diagnostic
                INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
                INNER JOIN Client ON Diagnosis.client_id = Client.id
                LEFT JOIN Event ON Diagnostic.event_id = Event.id AND Event.deleted = 0
                LEFT JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
                LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id
                LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
                LEFT JOIN ActionProperty_String ON ActionProperty.id = ActionProperty_String.id
               WHERE
                  %s AND
                  ActionType.code = '*1-0-7т'
                  AND ActionPropertyType.name = 'Вакцинация'
                  AND (rbDiagnosisType.code = 1
                  OR rbDiagnosisType.code = 1)
                  AND %s
                  AND ActionType.deleted = 0
                  AND ActionPropertyType.deleted = 0
                  AND Diagnostic.deleted = 0
               GROUP BY
                  CASE
                  WHEN ageClient BETWEEN 0 AND 14 THEN
                    1
                  WHEN ageClient BETWEEN 15 AND 17 THEN
                    2
                  WHEN ageClient BETWEEN 18 AND 29 THEN
                    3
                  WHEN ageClient BETWEEN 30 AND 39 THEN
                    4
                  WHEN ageClient BETWEEN 40 AND 49 THEN
                    5
                  WHEN ageClient BETWEEN 50 AND 59 THEN
                    6
                  WHEN ageClient BETWEEN 60 AND 69 THEN
                    7
                  WHEN ageClient > 70 THEN
                    8
                  END
                  WITH ROLLUP; ''' % (tableDiagnosis['MKB'].inlist(diagnosis), db.joinAnd(cond))

    return db.query(stmt)


class CReportProphilaxy(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по экстренной профилактике столбняка при травмах')

    def getSetupDialog(self, parent):
        dialog = CPrimaryRepeatHospitalization(parent)
        dialog.setTitle(self.title())
        dialog.cmbPerson.setVisible(False)
        dialog.lblPerson.setVisible(False)
        return dialog

    def build(self, params):

        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        isEventCreateParams = params.get('isEventCreateParams', False)
        eventBegDatetime =params.get('eventBegDatetime', None)
        eventEndDatetime = params.get('eventEndDatetime', None)
        eventTypeId = params.get('eventTypeId', None)
        query = selectData(begDate, endDate, isEventCreateParams, eventBegDatetime, eventEndDatetime, eventTypeId)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('%2',  [u'Кол-во лиц, обрат. по поводу травм с нарушен. целостности кожных покр.'],                                                                         CReportBase.AlignRight),
                        ('%5',  [u'Кол-во лиц, подлежащих экстренной проф.'], CReportBase.AlignLeft),
                        ('%5',  [u'В т.ч. мужчин'], CReportBase.AlignLeft),
                        ('%5',  [u'Из них получили экстренную профилактику',                                u'Всего'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'В том числе всего '], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'Вакцинация(не привитые в прошлом)',  u'0,5 АС+0,5 АДСМ+ППС'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'1.0АС+0.5АДМ+ПСС'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'1.0 АС+ПСС'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'0.5 АС+0.5АДСМ'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'1.0АС+0.5АДМ'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'1.0АС'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'Ревакцинация(привитые в прошлом)',   u'0.5АДСМ'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'0.5АС'], CReportBase.AlignLeft),
                        ('%5',  [u'Из них не получили Экстренную профилакт.',                               u'Всего'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'В том числе',                        u'Отказы'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'',                                   u'По вине Мед.раб.'], CReportBase.AlignLeft),
                        ('%5',  [u'Кол-во биопроб К белкуПСС'], CReportBase.AlignLeft),
                        ('%5',  [u'В том числе положительные'], CReportBase.AlignLeft),
                        ('%5',  [u'Кол-во реакций на Введение ПСС'], CReportBase.AlignLeft),
                        ('%5',  [u'В том числе',                                                            u'местная'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'аллергия'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                                       u'общая'], CReportBase.AlignLeft),
                        ('%5',  [u'кол-во лиц, получ. RV через 6-12 мес.'], CReportBase.AlignLeft),
                        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1) #Кол-во лиц, обрат. по поводу травм с
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(1, 5, 1, 6)
        table.mergeCells(1, 11, 1, 2)
        table.mergeCells(1, 13, 2, 1)
        table.mergeCells(1, 14, 1, 2)
        table.mergeCells(0, 16, 3, 1)
        table.mergeCells(0, 17, 3, 1)
        table.mergeCells(0, 18, 3, 1)
        table.mergeCells(0, 19, 1, 3)
        table.mergeCells(0, 22, 3, 1)
        table.mergeCells(0, 3, 1, 10)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(0, 13, 1, 3)
        table.mergeCells(1, 19, 2, 1)
        table.mergeCells(1, 20, 2, 1)
        table.mergeCells(1, 21, 2, 1)

        row = [u'0-14', u'15-17', u'18-29', u'30-39', u'40-49', u'50-59', u'60-69', u'70>', u'Итого']
        rowSize = 12
        total = [0]*rowSize
        i = 0
        while query.next():
            record = query.record()
            cnt = forceInt(record.value('cnt'))
            cntMen = forceInt(record.value('cntMen'))
            cntEvent = forceInt(record.value('cntEvent'))
            cntADCM = forceInt(record.value('cntADCM'))
            cntAC_ADCM_PCC = forceInt(record.value('cntAC_ADCM_PCC'))
            cntAC_ADM_PCC = forceInt(record.value('cntAC_ADM_PCC'))
            cntAC_PCC = forceInt(record.value('cntAC_PCC'))
            cntAC_ADMC = forceInt(record.value('cntAC_ADMC'))
            cntAC_ADM = forceInt(record.value('cntAC_ADM'))
            cntAC = forceInt(record.value('cntAC'))
            cntReADCM = forceInt(record.value('cntReADCM'))
            cntReAC = forceInt(record.value('cntReAC'))
            i = table.addRow()
            table.setText(i, 0, row[i-3])
            table.setText(i, 1, cnt)
            table.setText(i, 2, cntMen)
            table.setText(i, 3, cntEvent)
            table.setText(i, 4, cntADCM)
            table.setText(i, 5, cntAC_ADCM_PCC)
            table.setText(i, 6, cntAC_ADM_PCC)
            table.setText(i, 7, cntAC_PCC)
            table.setText(i, 8, cntAC_ADMC)
            table.setText(i, 9, cntAC_ADM)
            table.setText(i, 10, cntAC)
            table.setText(i, 11, cntReADCM)
            table.setText(i, 12, cntReAC)
        if not i:
            i = table.addRow()
            table.setText(i, 0, row[len(row) - 1])
            for index in xrange(rowSize):
                table.setText(i, index + 1, total[0])
        return doc
