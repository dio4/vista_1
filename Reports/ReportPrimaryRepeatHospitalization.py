# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceInt, forceString, getVal

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPrimaryRepeatHospitalization import Ui_ReportPrimaryRepeatHospitalization


diagnosisForHospitalization = [
    (u'Сотрясение головного мозга', u'S06.0', u'S06.2'),
    (u'Перелом костей черепа и лицевого скелета', u'S02.0', u'S02.1', u'S02.2', u'S.02.3', u'S02.4', u'S02.5', u'S02.6', u'S02.7', u'S02.8'),
    (u'Перелом костей позвоночника', u'S12.0', u'S12.1', u'S12.2', u'S12.7', u'S12.9', u'S22.0', u'S32.0', u'S32.1', u'S32.2'),
    (u'Перелом костей таза и бедренной кости', u'S32.3', u'S23.3', u'S32.5', u'S32.7',u'S32.8', u'S72.0', u'S72.3', u'S72.4', u'S72.9'),
    (u'Перелом ключицы и лопатки', u'S42.0', u'S42.3'),
    (u'Перелом, переломвывихи плечевой кости', u'S43.0', u'S42.3'),
    (u'Перелом шейки плечевой кости', u'S42.2'),
    (u'Перелом диафиза плеча', u'S42.4'),
    (u'Перелом костей голени', u'S82.1', u'S82.2', u'S82.3', u'S82.4', u'S82.8', u'S82.7'),
    (u'Перелом лодыжек с вывехом кости', u'S82.5', u'S82.6'),
    (u'Перелом надколенника', u'S82.0'),
    (u'Перелом пяточной кости', u'S92.0'),
    (u'Множественные переломы ребер', u'S22.4'),
    (u'Проникающие ранения полостей', u''),
    (u'Обширные ожоги и обморожения', u'T20.', u'T33', u'T20', u'T22', u'T21', u'T23', u'T24', u'T25', u'T29', u'T26', u'T33.0', u'T33.5', u'T33.8'),
    (u'Обширные раны мягких тканей', u'T01.8', u'S01.0', u'S01.1', u'S01.2', u'S01.3', u'S01.4', u'S01.5', u'S01.7', u'S01.8', u'S01.9',
                                     u'S11.8', u'S21.0', u'S21.1', u'S21.2', u'S21.7', u'21.8', u'21.9', u'S31.0', u'S31.1', u'S31.2' u'S31.3', u'S71.0', u'S71.1',
                                     u'S81.0', u'S81.7', u'S81.8', u'S91.0', u'S91.1', u'S91.3', u'S41.0', u'S41.1', u'S41.7', u'S51.0', u'S51.7', u'S51.8', u'S61.0',
                                     u'S61.8', u'S67.0', u'S67.8', u'S68.0', u'S68.1', u'S68.'),
    (u'Подкожные разрывы мышц', u'S29.0', u'S86.1', u'S46.', u'S29.0'),
    (u'Повреждение сухожилий сгибателей пальцев кисти', u'S66.0'),
    (u'Прочие', u'T17.2', u'T16.0', u'T17.1', u'S05', u'S05.1', u'S05.5', u'S05.6', u'S03.0', u'S13.1', u'S22.2', u'S23.1', u'S36.0', u'S37.0', u'S73.0', u'S86.0',
                u'S83.2', u'S83.0', u'S92.0', u'S92.1', u'S92.2', u'S92.3', u'S98.0', u'S98.1', u'98.2', u'S93.', u'S43.5', u'S52.0', u'S52.1', u'S52.2', u'S52.3',
                u'S52.4', u'S52.5', u'S52.6', u'S52.7', u'S52.8', u'S52.9', u'S53.1', u'S62.0', u'S62.1', u'S62.2', u'S62.3', u'S62.4', u'S62.4', u'S63.0', u'S63.1',
                u'S67.0', u'S67.8', u'S68.0', u'S68.1', u'S68', u'T00.8')
]

diagnosis = [
    (u'Переломы костей черепа, туловища, позвоночника', u'S02.0', u'S02.1', u'S02.2', u'S02.3', u'S02.4', u'S02.5', u'S02.6', u'S02.7', u'S02.8', u'S12.0', u'S12.1',
                                                        u'S12.2', u'S12.7', u'S12.9', u'S22.0', u'S32.0', u'S32.1', u'S32.2', u'S32.3', u'S32.5', u'S32.7', u'S32.8',
                                                        u'S22.2', u'S22.3', u'S22.4', u'S42.0', u'S42.1', u'S32.4'),
    (u'Переломы крупных костей н/конечностей и в/конечностей: плечевая, бедренная, кости голени и предплечья',u'S72.0',u'S72.3',u'S72.4',u'S72.9',u'S82.2',u'S82.3',u'S82.4',u'S82.5',u'S82.6',u'S82.7',u'S82.8',u'S42.2',u'S42.3',u'S42.4',u'S52.0',u'S52.1',u'S52.2'u'S52.3',u'S52.4',u'S52.5',u'S52.6',u'S52.7',u'S52.8',u'S52.9'),
    (u'Переломы мелких костей нижних иверхних конечностей (не указанные ранее)', u'S82.0', u'S82.1', u'S92.0', u'S92.1', u'S92.2', u'S92.3', u'S92.4', u'S92.5', u'S92.7',
                                                                                 u'S62.0', u'S62.1', u'S62.2', u'S62.3', u'S62.4', u'S62.5', u'S62.6', u'S62.7', u'S68.0',
                                                                                 u'S68.1', u'S68.', u'S98.0', u'S98.1', u'S98.2', u'S93'),
    (u'Вывихи суставов', u'S03.0', u'S13.1', u'S23.1', u'S73.0', u'S83.0', u'S93.0', u'S93.1', u'S93.3', u'S43.0', u'S43.5', u'S53.1', u'S63.0', u'S63.1'),
    (u'Внутричерепная травма', u'S06.0', u'S06.2'),
    (u'Раны мягких тканей', u'T01.8', u'S01.0', u'S01.1', u'S01.2', u'S01.3', u'S01.4', u'S01.5', u'S01.7',
                            u'S01.8', u'S01.9', u'S11.8', u'S21.0', u'S21.1', u'S21.2', u'S21.7', u'S21.8', u'S21.9', u'S31.0', u'S31.1',
                            u'S31.3', u'S71.0', u'S71.1', u'S81.0', u'S81.7', u'S81.8', u'S91.0', u'S91.1', u'S91.3', u'S41.0', u'S41.1', u'S41.7',
                            u'S51.0', u'S51.7', u'S51.8', u'S61.0', u'S61.8', u'S67.0', u'S67.8', u'S68.0', u'S68.1', u'S68'),
    (u'Ушибы и растяжения связок', u'T00.8', u'S00.0', u'S00.1', u'S00.3', u'S00.4', u'S00.5', u'S00.7', u'S00.8', u'S10.', u'S10.7', u'S10.8', u'S10.9', u'S13.4',
                                   u'S20.2', u'S20.2', u'S20.7', u'S30.0', u'S30.1', u'S30.8', u'S33.7', u'S70.0', u'S70.1', u'S70.8', u'S73', u'S80.8', u'S80.1',
                                   u'S80.8', u'S83.6', u'S90.0', u'S90.3', u'S90.1', u'S90.8', u'S93.4', u'S93.5', u'S93.6', u'S40.0', u'S40.8', u'S40.7', u'S50.0',
                                   u'S50.1', u'S53.', u'S60.0', u'S60.2', u'S60.7', u'S63.3', u'S63.4', u'S63.5', u'S63.6', u'S63.7'),
    (u'Инородные тела (в т.ч. укусы клещей)', u'B88.9', u'T17.2', u'T16.0', u'T17.1'),
    (u'Ожоги и обморожения', u'T20', u'T21',u'T22', u'T23', u'T24', u'T25', u'T29', u'T26', u'T33', u'T33.0', u'T33.5', u'T33.8'),
    (u'Глазная травма', u'S05', u'S50.1', u'S05.5', u'S05.6'),
    (u'Заболевания', u''),
    (u'Прочие' , u'S29.0', u'S23.3', u'S30.1', u'S36.0', u'S37.0', u'S86.0', u'S83.2', u'S86.1', u'S93.2', u'S40.8', u'S40.7', u'S46.0', u'S50.8', u'S60.8', u'S63.3',
                 u'S63.4', u'S63.5', u'S66.0'),
    (u'Не травма', u'')
]

def selectData(begDate, endDate, isEventCreateParams, eventBegDatetime, eventEndDatetime, eventTypeId, personId, hospitalization):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableDiagnosis = db.table('Diagnosis')
    tableDiagnostic = db.table('Diagnostic')

    additionalFrom = ''
    additionalSelect = ''
    cond = [db.joinOr([tableDiagnosis['MKB'].like('T%'), tableDiagnosis['MKB'].like('S%')])]

    if personId and not hospitalization:
        cond.append(tableEvent['person_id'].eq(personId))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if isEventCreateParams:
        cond.append(tableEvent['createDatetime'].dateGe(eventBegDatetime))
        cond.append(tableEvent['createDatetime'].dateLe(eventEndDatetime))
    else:
        cond.append(tableEvent['setDate'].dateGe(begDate))
        cond.append(tableEvent['setDate'].dateLe(endDate))
    if hospitalization:
        additionalSelect = u''' , count(DISTINCT if(ActionProperty_String.value = 'первично', Event.id, NULL)) AS countPrimary
                                , count(DISTINCT if(ActionProperty_String.value = 'повторно', Event.id, NULL)) AS countRepeat'''
        additionalFrom = u'''INNER JOIN ActionType ON ActionType.code = '*1-0-4т' AND ActionType.deleted = 0
                             INNER JOIN Action ON Action.deleted = 0 AND Action.actionType_id = ActionType.id AND Action.event_id = Event.id
                             INNER JOIN ActionPropertyType ON ActionPropertyType.name = 'Порядок госпитализации' AND ActionPropertyType.deleted = 0
                             INNER JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id
                             INNER JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id'''
    cond.append(db.joinAnd([tableEvent['deleted'].eq(0), tableDiagnosis['deleted'].eq(0), tableDiagnostic['deleted'].eq(0)]))

    stmt = u'''SELECT Diagnosis.MKB
                      , count(DISTINCT Event.id) AS countClient
                      %s
                FROM
                  Event
                  %s
                  INNER JOIN rbDiagnosisType ON rbDiagnosisType.code = '1' OR rbDiagnosisType.code = '2'
                  LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.diagnosisType_id = rbDiagnosisType.id
                  LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                WHERE %s
                GROUP BY
                    Diagnosis.MKB
            ''' % (additionalSelect, additionalFrom, db.joinAnd(cond))
    return db.query(stmt)

class CReportPrimaryRepeatHospitalization(CReport):
    def __init__(self, parent, hospitalization = False):
        CReport.__init__(self, parent)
        self.hospitalization = hospitalization
        if self.hospitalization:
            self.setTitle(u'Структура госпитализации первично и повторно обратившихся пострадавших')
            self.diagnosis = diagnosisForHospitalization
        else:
            self.setTitle(u'Структура обращаемости по основным нозологическим группам')
            self.diagnosis = diagnosis

    def getSetupDialog(self, parent):
        dialog = CPrimaryRepeatHospitalization(parent)
        dialog.setTitle(self.title())
        if self.hospitalization:
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
        personId = params.get('personId', None)
        query = selectData(begDate, endDate, isEventCreateParams, eventBegDatetime, eventEndDatetime, eventTypeId, personId, self.hospitalization)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('35%', [u'Диагноз при поступлении'],       CReportBase.AlignRight),
                        ('35%', [u'MKB'],  CReportBase.AlignLeft),
                        ('15%',[u'Количество'],     CReportBase.AlignLeft),
                        ]
        if self.hospitalization:
            tableColumns.append(('15%',[u'Количество первичных больных'],     CReportBase.AlignLeft))
            tableColumns.append(('15%',[u'Количество повторных больных'],     CReportBase.AlignLeft))

        table = createTable(cursor, tableColumns)
        resultTable, total = self.getTable(query)
        for key in sorted(resultTable.keys()):
            i = table.addRow()
            table.setText(i, 0, key)
            table.setText(i, 1, resultTable[key][3])
            table.setText(i, 2, resultTable[key][0])
            if self.hospitalization:
                table.setText(i, 3, resultTable[key][1])
                table.setText(i, 4, resultTable[key][2])
        i = table.addRow()
        table.setText(i, 0, u'ИТОГО', CReportBase.TableTotal)
        table.setText(i, 2, total[0], CReportBase.TableTotal)
        if self.hospitalization:
            table.setText(i, 3, total[1], CReportBase.TableTotal)
            table.setText(i, 4, total[2], CReportBase.TableTotal)
        return doc

    def getTable(self, query):
        table = {}
        total = [0]*3
        while query.next():
            record = query.record()
            MKB = forceString(record.value('MKB'))
            countClient = forceInt(record.value('countClient'))
            countPrimary = forceInt(record.value('countPrimary'))
            countRepeat = forceInt(record.value('countRepeat'))
            for index in xrange(len(self.diagnosis)):
                key = forceString(self.diagnosis[index][0])
                if not self.diagnosis[index][0] in table.keys():
                    table[key] = [0]*4
                    table[key][3] = forceString(self.diagnosis[index][1:])
                    table[key][3] = table[key][3].replace("'", '')
                    table[key][3] = table[key][3].replace("u", '')
                    table[key][3] = table[key][3].replace("(", '')
                    table[key][3] = table[key][3].replace(")", '')
                    table[key][3] = table[key][3].replace(",", ' ')
                if self.diagnosis[index].count(MKB):
                    table[key][0] += countClient
                    table[key][1] += countPrimary
                    table[key][2] += countRepeat
                    total[0] += countClient
                    total[1] += countPrimary
                    total[2] += countRepeat
                    break
        return table, total

class CPrimaryRepeatHospitalization (QtGui.QDialog, Ui_ReportPrimaryRepeatHospitalization):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.gbEventDatetimeParams.setChecked(params.get('isEventCreateParams', False))
        self.edtEventBegDatetime.setDateTime(params.get('eventBegDatetime', QtCore.QDateTime.currentDateTime()))
        self.edtEventEndDatetime.setDateTime(params.get('eventEndDatetime', QtCore.QDateTime.currentDateTime()))
        self.cmbPerson.setValue(getVal(params, 'personId', None))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['isEventCreateParams'] = self.gbEventDatetimeParams.isChecked()
        params['eventBegDatetime']  = self.edtEventBegDatetime.dateTime()
        params['eventEndDatetime']  = self.edtEventEndDatetime.dateTime()
        params['eventTypeId'] = self.cmbEventType.value()
        params['personId'] = self.cmbPerson.value()
        return params