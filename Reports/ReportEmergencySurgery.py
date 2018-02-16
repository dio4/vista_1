# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString, forceDouble
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


diseaseList = [u'Острый аппендицит',
               u'Острая кишечная непроходимость',
               u'Ущемлённая грыжа',
               u'Пробод. фзва жел. и 12-п кишки',
               u'Желудчно-кишечное кровотечение',
               u'Острый холецистит',
               u'Острый панкреатит']

timeList = [u'До 6 ч',
            u'7 - 24 ч',
            u'> 24 ч']

def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    endDiagnosis = forceInt(params.get('endDiagnosis'))
    
    if endDiagnosis == 0:
        diagnoseSource = u'''
            LEFT JOIN Action as diagnoseSource ON diagnoseSource.id = act.id
        '''
    else:
        diagnoseSource = u'''
            LEFT JOIN Diagnostic ON Diagnostic.id IN (SELECT diagnosticTemp.id
                                                      FROM Diagnostic AS diagnosticTemp
                                                      INNER JOIN rbDiagnosisType AS rbDiagnosisTypeTemp ON rbDiagnosisTypeTemp.id = diagnosticTemp.diagnosisType_id
                                                      WHERE diagnosticTemp.event_id = Event.id
                                                            AND diagnosticTemp.deleted = 0
                                                            AND rbDiagnosisTypeTemp.code = IF((SELECT COUNT(diagnosticTempLow.id)
                                                                                               FROM Diagnostic AS diagnosticTempLow
                                                                                               INNER JOIN rbDiagnosisType AS rbDiagnosisTypeTempLow ON rbDiagnosisTypeTempLow.id = diagnosticTempLow.diagnosisType_id
                                                                                               WHERE diagnosticTempLow.event_id = Event.id
                                                                                                     AND diagnosticTempLow.deleted = 0
                                                                                                     AND rbDiagnosisTypeTempLow.code = 1
                                                                                               GROUP BY diagnosticTempLow.id) > 0, 1, 2))
            LEFT JOIN Diagnosis AS diagnoseSource ON diagnoseSource.id = Diagnostic.diagnosis_id
                AND diagnoseSource.deleted = 0
        '''
    stmt = u'''
        SELECT
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 1_1_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NULL, Event.id, NULL)) as 1_1_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NULL
                                    AND %(dead)s, Event.id, NULL)) as 1_1_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 1_1_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 1_1_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 1_1_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 1_1_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 1_2_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NULL, Event.id, NULL)) as 1_2_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NULL
                                    AND %(dead)s, Event.id, NULL)) as 1_2_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 1_2_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 1_2_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 1_2_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 1_2_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 1_3_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NULL, Event.id, NULL)) as 1_3_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NULL
                                    AND %(dead)s, Event.id, NULL)) as 1_3_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 1_3_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 1_3_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 1_3_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321010', '321020', '321400', '321040', '321420')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 1_3_11,

            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 2_1_3,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 2_1_4,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 2_1_5,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 2_1_6,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 2_1_7,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 2_1_10,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 2_1_11,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 2_2_3,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 2_2_4,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 2_2_5,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 2_2_6,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 2_2_7,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 2_2_10,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 2_2_11,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 2_3_3,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 2_3_4,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 2_3_5,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 2_3_6,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 2_3_7,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 2_3_10,
            COUNT(DISTINCT IF(mes.MES.code = '321050'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 2_3_11,

            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 3_1_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 3_1_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 3_1_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 3_1_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 3_1_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 3_1_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 3_1_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 3_2_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 3_2_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 3_2_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 3_2_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 3_2_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 3_2_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 3_2_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 3_3_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 3_3_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 3_3_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 3_3_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 3_3_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 3_3_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321230', '321240', '321250', '321490', '321480')
                                    AND atExc.code IN ('630806', '630807', '630808', '640810', '640812', '650521', '650812', '650839', '630840', '640801', '640808', '651308', 'ож001', '0ж002', 'ож002а', 'ож003', 'ож003а', 'ож004', 'ож004а')
                                    AND Event.order = 2
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 3_3_11,

            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 4_1_3,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 4_1_4,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 4_1_5,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 4_1_6,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 4_1_7,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 4_1_10,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 4_1_11,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 4_2_3,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 4_2_4,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 4_2_5,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 4_2_6,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 4_2_7,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 4_2_10,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 4_2_11,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 4_3_3,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 4_3_4,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 4_3_5,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 4_3_6,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 4_3_7,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 4_3_10,
            COUNT(DISTINCT IF(diagnoseSource.MKB IN ('K25.1', 'K25.5', 'K25.6', 'K26.1', 'K26.5', 'K26.6', 'K27.1', 'K27.5', 'K27.6')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 4_3_11,

            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 5_1_3,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 5_1_4,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 5_1_5,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 5_1_6,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 5_1_7,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 5_1_10,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 5_1_11,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 5_2_3,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 5_2_4,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 5_2_5,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 5_2_6,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 5_2_7,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 5_2_10,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 5_2_11,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 5_3_3,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 5_3_4,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 5_3_5,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 5_3_6,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 5_3_7,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 5_3_10,
            COUNT(DISTINCT IF(mes.MES.code = '321150'
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 5_3_11,

            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 6_1_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 6_1_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 6_1_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 6_1_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 6_1_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 6_1_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 6_1_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 6_2_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 6_2_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 6_2_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 6_2_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 6_2_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 6_2_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 6_2_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 6_3_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 6_3_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 6_3_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 6_3_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 6_3_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 6_3_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('321440', '321060', '321070')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 6_3_11,

            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов'), Event.id, NULL)) as 7_1_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 7_1_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 7_1_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 7_1_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 7_1_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6, Event.id, NULL)) as 7_1_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) <= 6
                                    AND %(dead)s, Event.id, NULL)) as 7_1_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('7-12 часов', '7-24 часов'), Event.id, NULL)) as 7_2_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 7_2_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 7_2_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 7_2_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value IN ('7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 7_2_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24, Event.id, NULL)) as 7_2_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) BETWEEN 7 AND 24
                                    AND %(dead)s, Event.id, NULL)) as 7_2_11,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов'), Event.id, NULL)) as 7_3_3,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL, Event.id, NULL)) as 7_3_4,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS  NULL
                                    AND %(dead)s, Event.id, NULL)) as 7_3_5,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL, Event.id, NULL)) as 7_3_6,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND aps.value NOT IN ('1 час', '2 часа', '3 часа', '4 часа', '5 часов', '6 часов', '7-12 часов', '7-24 часов')
                                    AND actExc.id IS NOT NULL
                                    AND %(dead)s, Event.id, NULL)) as 7_3_7,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24, Event.id, NULL)) as 7_3_10,
            COUNT(DISTINCT IF(mes.MES.code IN ('311200', '311210', '311220')
                                    AND actExc.id IS NOT NULL
                                    AND TIMESTAMPDIFF(HOUR, Event.setDate, actExc.begDate) > 24
                                    AND %(dead)s, Event.id, NULL)) as 7_3_11
        FROM Event
        LEFT JOIN Action as act ON Event.id = act.event_id
                    AND act.deleted = 0
                    AND act.id = (SELECT actMov.id
                                    FROM Action as actMov
                                    INNER JOIN ActionType as atMov ON actMov.actionType_id = atMov.id
                                            AND atMov.flatCode LIKE 'moving'
                                            AND atMov.deleted = 0
                                    WHERE actMov.event_id = Event.id
                                            AND actMov.deleted = 0
                                    ORDER BY actMov.begDate DESC LIMIT 1)
        %(diagnoseSource)s
        LEFT JOIN Action as actExc ON actExc.id = (SELECT actExc1.id
                                FROM Action actExc1
                                INNER JOIN ActionType atExc1 ON atExc1.id = actExc1.actionType_id
                                WHERE actExc1.event_id = Event.id AND actExc1.deleted = 0 AND atExc1.deleted = 0
                                        AND (atExc1.code LIKE '6%%' OR atExc1.code LIKE 'о%%')
                                LIMIT 1)
        LEFT JOIN ActionType as atExc ON atExc.id = actExc.actionType_id AND atExc.deleted = 0
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        LEFT JOIN ActionType as atRec ON atRec.deleted = 0
                AND atRec.flatCode LIKE 'received'
        LEFT JOIN Action as actRec ON actRec.event_id = Event.id AND actRec.actionType_id = atRec.id
                AND actRec.deleted = 0

        LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = atRec.id AND ActionPropertyType.name = 'Доставлен'
                AND ActionPropertyType.deleted = 0
        LEFT JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = actRec.id
                AND ActionProperty.deleted = 0
        LEFT JOIN ActionProperty_String as aps ON aps.id = ActionProperty.id
        LEFT JOIN mes.MES ON mes.MES.id = act.MES_id AND mes.MES.deleted = 0
        WHERE
            DATE(Event.execDate) >= DATE('%(begDate)s') AND DATE(Event.execDate) <= DATE('%(endDate)s')
            AND Event.deleted = 0
        ''' %  {'diagnoseSource' : diagnoseSource,
                'begDate' : forceString(begDate.toString('yyyy-MM-dd')),
                'endDate' : forceString(endDate.toString('yyyy-MM-dd')),
                'dead' : "rbResult.regionalCode IN ('5', '11')"}

    db = QtGui.qApp.db
    return db.query(stmt)

class CReportEmergencySurgery(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения по экстренной хирургической помощи')

    def getSetupDialog(self, parent):
        result = CReportEmergencySurgerySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def dumpParams(self, cursor, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())

        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result

        description = []
        if begDate and endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))

        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def getStringValue(self, record, index, number, numberTimeList):
        return forceString(record.value(forceString(number) + '_' + forceString(numberTimeList + 1) + '_' + forceString(index)))

    def getIntValue(self, record, index, number, numberTimeList):
        return forceInt(record.value(forceString(number) + '_' + forceString(numberTimeList + 1) + '_' + forceString(index)))

    def getFloatValue(self, record, index, number, numberTimeList):
        return forceDouble(record.value(forceString(number) + '_' + forceString(numberTimeList + 1) + '_' + forceString(index)))

    def outputCount(self, table, i, record, number, numberTimeList, localSumm, totalSumm):

        values = [self.getStringValue(record, idx, number, numberTimeList) or u'0' for idx in xrange(14)]
        if forceInt(values[3]):
            values[8] = forceString(int((forceDouble(values[5]) + forceDouble(values[7])) * 100 / forceDouble(values[3]) + 0.5)) #add 0.5 to round to nearest integer
            values[12] = forceString(int(forceDouble(values[11]) * 100 / forceDouble(values[3]) + 0.5))
        if forceInt(values[10]):
            values[13] = forceString(int(forceDouble(values[11]) * 100 / forceDouble(values[10]) + 0.5))
        values[2] = values[9] = timeList[numberTimeList]
        for idx in xrange(2, 14):
            table.setText(i, idx, values[idx])
        for idx in xrange(5):
            localSumm[idx] += forceInt(values[idx + 3])
            totalSumm[numberTimeList][idx] += forceInt(values[idx + 3])
        for idx in (5, 6):
            localSumm[idx] += forceInt(values[idx + 5])
            totalSumm[numberTimeList][idx] += forceInt(values[idx + 5])

    def outputLocalSumm(self, table, localSumm):
        row = table.addRow()
        table.setText(row, 2, u'Итого:')
        for idx in xrange(5):
            table.setText(row, idx + 3, forceString(localSumm[idx]))
        if localSumm[0]:
            table.setText(row, 8, forceString((localSumm[2] + localSumm[4]) * 100 / localSumm[0]))
        else:
            table.setText(row, 8, u'0')
        table.setText(row, 10, forceString(localSumm[5]))
        table.setText(row, 11, forceString(localSumm[6]))
        if localSumm[0]:
            table.setText(row, 12, forceString(localSumm[6] * 100 / localSumm[0]))
        else:
            table.setText(row, 12, u'0')
        if localSumm[5]:
            table.setText(row, 13, forceString(localSumm[6] * 100 / localSumm[5]))
        else:
            table.setText(row, 13, u'0')

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сведения по экстренной хирургической помощи по 7-ми формам "острого живота" для отдела организации скорой помощи НИИ им. проф. И.И. Джанилидзе')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'№', u'', u''],                   CReportBase.AlignCenter),
            ('25%', [u'Нозологические формы', u'', u''],   CReportBase.AlignCenter),
            ('10%', [u'Срок доставки', u'', u''],        CReportBase.AlignCenter),
            ('10%', [u'Выбыло', u'Всего', u''],          CReportBase.AlignCenter),
            ('5%', [u'', u'Не оперировано', u'Всего'],   CReportBase.AlignCenter),
            ('5%', [u'', u'', u'Умерло'],                CReportBase.AlignCenter),
            ('5%', [u'', u'Оперировано', u'Всего'],      CReportBase.AlignCenter),
            ('5%', [u'', u'', u'Умерло'],                CReportBase.AlignCenter),
            ('5%', [u'Летальность (общ.) %', u''],      CReportBase.AlignCenter),
            ('5%', [u'Срок операции', u''],      CReportBase.AlignCenter),
            ('5%', [u'Всего оперировано', u''],      CReportBase.AlignCenter),
            ('5%', [u'Из них умерло', u''],      CReportBase.AlignCenter),
            ('5%', [u'Летальность', u'(общ.) %'],      CReportBase.AlignCenter),
            ('5%', [u''           , u'П/о %'],      CReportBase.AlignCenter),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 5)
        table.mergeCells(0, 8, 3, 1)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(0, 9, 3, 1)
        table.mergeCells(0, 10, 3, 1)
        table.mergeCells(0, 11, 3, 1)
        table.mergeCells(0, 12, 1, 2)

        row = table.addRow()
        for colNum in xrange(14):
            table.setText(row, colNum, forceString(colNum))
        query = selectData(params)
        number = 1
        totalSumm = [[0]*7, [0]*7, [0]*7]
        self.setQueryText(forceString(query.lastQuery()))
        if query.first():
            record = query.record()
            while number <= 7:
                localSumm = [0, 0, 0, 0, 0, 0, 0]
                numberTimeList = 0
                row = table.addRow()
                table.setText(row, 0, number)
                table.setText(row, 1, diseaseList[number - 1])
                self.outputCount(table, row, record, number, numberTimeList, localSumm, totalSumm)
                row = table.addRow()
                numberTimeList = 1
                self.outputCount(table, row, record, number, numberTimeList, localSumm, totalSumm)
                row = table.addRow()
                numberTimeList = 2
                self.outputCount(table, row, record, number, numberTimeList, localSumm, totalSumm)
                self.outputLocalSumm(table, localSumm)
                table.mergeCells(row - 2, 0, 4, 1)
                table.mergeCells(row - 2, 1, 4, 1)
                number += 1

        numberTimeList = 0
        localSumm = [0, 0, 0, 0, 0, 0, 0]
        while numberTimeList <= 2:
            row = table.addRow()
            table.setText(row, 2, timeList[numberTimeList])
            for idx in xrange(5):
                table.setText(row, idx + 3, forceString(totalSumm[numberTimeList][idx]))
            if totalSumm[numberTimeList][0]:
                table.setText(row, 8, forceString(forceInt((totalSumm[numberTimeList][2] + totalSumm[numberTimeList][4]) * 100.0 / totalSumm[numberTimeList][0] + 0.5)))
            else:
                table.setText(row, 8, u'0')
            table.setText(row, 9, timeList[numberTimeList])
            table.setText(row, 10, forceString(totalSumm[numberTimeList][5]))
            table.setText(row, 11, forceString(totalSumm[numberTimeList][6]))
            if totalSumm[numberTimeList][0]:
                table.setText(row, 12, forceString(forceInt(totalSumm[numberTimeList][6] * 100.0 / totalSumm[numberTimeList][0] + 0.5)))
            else:
                table.setText(row, 12, u'0')
            if totalSumm[numberTimeList][5]:
                table.setText(row, 13, forceString(forceInt(totalSumm[numberTimeList][6] * 100 / totalSumm[numberTimeList][5] + 0.5)))
            else:
                table.setText(row, 13, u'0')
            for idx in xrange(7):
                localSumm[idx] += totalSumm[numberTimeList][idx]
            numberTimeList += 1
        table.setText(row, 1, u'ИТОГО:')
        self.outputLocalSumm(table, localSumm)
        table.mergeCells(row - 2, 0, 4, 2)

        return doc

from Ui_ReportEmergencySurgerySetup import Ui_ReportEmergencySurgerySetupDialog

class CReportEmergencySurgerySetupDialog(QtGui.QDialog, Ui_ReportEmergencySurgerySetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        pass
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEndDiagnosis.setCurrentIndex(params.get('endDiagnosis', 0))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['endDiagnosis'] = self.cmbEndDiagnosis.currentIndex()
        
        return result