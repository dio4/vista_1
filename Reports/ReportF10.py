# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils       import forceDate, forceInt, forceString, forceBool
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase


def selectData(params, numberDiagnosis, join, where):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    isRegistry = forceBool(params.get('isRegistry'))
    nextYear = forceString(forceInt(endDate.toString('yyyy')) + 1) + '-01-01'
    columnQuery = [0, 14,
                   15, 17,
                   18, 19,
                   20, 39,
                   40, 59,
                   60]
    select = u'''COUNT(DISTINCT Client.id) AS countAll,
                COUNT(DISTINCT IF(Client.sex = 2, Client.id, NULL)) AS countAllFemale,
                COUNT(DISTINCT IF(rbClientMonitoringKind.code LIKE 'К', Client.id, NULL)) AS countAllK,
                COUNT(DISTINCT IF(rbClientMonitoringKind.code LIKE 'Д', Client.id, NULL)) AS countAllD,'''
    j = 0
    while j < len(columnQuery) - 1:
        select += u'''\nCOUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') >= %s
            AND TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') <= %s, Client.id, NULL)) AS count%s, ''' % (nextYear, columnQuery[j], nextYear, columnQuery[j + 1], columnQuery[j + 1])
        j += 2
    select += u'''\nCOUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') >= %s, Client.id , NULL)) AS count%s ''' % (nextYear, columnQuery[j], columnQuery[j])
    joinWhereDiagnosis = ''
    if len(numberDiagnosis) > 0:
        joinWhereDiagnosis = u'''AND ('''
        for mkb in numberDiagnosis:
            joinWhereDiagnosis += u'''Diagnosis.MKB LIKE '%s' OR ''' % mkb
        joinWhereDiagnosis += u'''False)'''
    if isRegistry:
        joinWhereEvent = ''
    else:
        joinWhereEvent = u'''LEFT JOIN Event ON Event.client_id = Client.id AND Event.deleted = 0
                             AND ((DATE(Event.setDate) >= DATE('%s') AND DATE(Event.setDate) <= DATE('%s'))
                             OR (DATE(Event.execDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s'))
                             OR (DATE(Event.setDate) <= DATE('%s') AND DATE(Event.execDate) >= DATE('%s')))''' % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))

    # joinWhereClientAttach = u'''AND DATE(clatMain.begDate) >= DATE('%s') AND DATE(clatMain.begDate) <= DATE('%s')''' % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))

    joinWhereClientMonitoring = u'''AND (ClientMonitoring.endDate IS NULL OR DATE(ClientMonitoring.endDate) >= DATE('2200-01-01'))'''

    # if isRegistry:
    #     where += u'''AND (clatMain.id IS NOT NULL
    #                OR (rbClientMonitoringKind.code LIKE 'К' AND clatMain.id IS NULL AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))
    #                OR (rbClientMonitoringKind.code LIKE 'Д' AND clatMain.id IS NULL AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))) '''
    # else:
    #     where += u'''AND ((clatMain.id IS NOT NULL AND Event.id IS NOT NULL)
    #                OR (rbClientMonitoringKind.code LIKE 'К' AND clatMain.id IS NULL AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))
    #                OR (rbClientMonitoringKind.code LIKE 'Д' AND clatMain.id IS NULL AND Event.id IS NOT NULL AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))) '''

    if isRegistry:
        where += u'''AND ((rbClientMonitoringKind.code LIKE 'К' AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))
                   OR (rbClientMonitoringKind.code LIKE 'Д' AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))) '''
    else:
        where += u'''AND (Event.id IS NOT NULL
                   OR (rbClientMonitoringKind.code LIKE 'К' AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))
                   OR (rbClientMonitoringKind.code LIKE 'Д' AND Event.id IS NOT NULL AND (Diagnostic.endDate IS NULL OR DATE(Diagnostic.endDate) >= DATE('2200-01-01')))) '''
    stmt = u'''
        SELECT %s
        FROM Client
        INNER JOIN Diagnosis ON Diagnosis.client_id = Client.id
                                AND Diagnosis.deleted = 0
                                AND Diagnosis.id = (SELECT MAX(diagTemp.id)
                                                    FROM Diagnosis AS diagTemp
                                                    INNER JOIN rbDiagnosisType AS diagnosisTypeTemp ON diagnosisTypeTemp.id = diagTemp.diagnosisType_id
                                                                                                       AND (diagnosisTypeTemp.code = 2 OR diagnosisTypeTemp.code = 1)
                                                    WHERE diagTemp.client_id = Client.id AND diagTemp.deleted = 0)
                                %s
        INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id AND Diagnostic.deleted = 0
        %s
        LEFT JOIN ClientMonitoring ON ClientMonitoring.client_id = Client.id %s
        LEFT JOIN rbClientMonitoringKind ON rbClientMonitoringKind.id = ClientMonitoring.kind_id
        %s
        WHERE Client.deleted = 0
              %s
    ''' % (select, joinWhereDiagnosis, joinWhereEvent, joinWhereClientMonitoring, join, where) #joinWhereClientAttach,

        # LEFT JOIN ClientAttach AS clatMain ON clatMain.id = (SELECT MAX(clatTemp.id)
        #                                                      FROM ClientAttach AS clatTemp
        #                                                      WHERE clatTemp.deleted = 0
        #                                                            AND clatTemp.client_id = Client.id
        #                                                            AND clatTemp.id = (SELECT MAX(clatTempLow.id)
        #                                                                               FROM ClientAttach AS clatTempLow
        #                                                                               INNER JOIN rbAttachType ON rbAttachType.id = clatTempLow.attachType_id AND rbAttachType.outcome = 1
        #                                                                               WHERE clatTempLow.deleted = 0 AND clatTempLow.client_id = Client.id))
        #                                       %s

    return db.query(stmt)


class CReportF10(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о заболеваниях психическими расстройствами и расстройствами поведения (кроме заболеваний, связанных с употреблением психоактивных веществ)')

    def getSetupDialog(self, parent):
        result = CReportF10SetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        rowNameSet = [[u'Психические расстройства (всего)', u'F00-F09, F20-F99', u'1',
                       ['F0%', 'F2%', 'F3%', 'F4%', 'F5%', 'F6%', 'F7%', 'F8%', 'F9%'],
                       '',
                       ''],
                     [u'Психозы и состояния слабоумия', u'F00-F05, F06(часть), F09, F20-25, F28, F29, F3x.x4, F30-F39(часть), F80.31, F84.0-.4, F99.1', u'2',
                       ['F00%', 'F01%', 'F02%', 'F03%', 'F04%', 'F05%', 'F09%', 'F06.0%', 'F06.1%', 'F06.2%', 'F06.30%', 'F06.31%', 'F06.32%', 'F06.33%', 'F06.81%', 'F06.91%', 'F20%', 'F21%', 'F22%', 'F23%', 'F24%', 'F25%', 'F28%', 'F29%', 'F39%', 'F30.24%', 'F31.24%', 'F31.54%', 'F32.34%', 'F33.34%', 'F30.23%', 'F30.24%', 'F30.25%', 'F30.26%', 'F30.27%', 'F30.28%', 'F31.23%', 'F31.24%', 'F31.25%', 'F31.26%', 'F31.27%', 'F31.28%', 'F31.53%', 'F31.54%', 'F31.55%', 'F31.56%', 'F31.57%', 'F31.58%', 'F32.33%', 'F32.34%', 'F32.35%', 'F32.36%', 'F32.37%', 'F32.38%', 'F33.33%', 'F33.34%', 'F33.35%', 'F33.36%', 'F33.37%', 'F33.38%', 'F80.31%', 'F84.0%', 'F84.1%', 'F84.2%', 'F84.3%', 'F84.4%', 'F99.1%'],
                       '',
                       ''],
                     [u'  в том числе:\nорганические психозы и (или) слабоумие', u'F00-F05, F06(часть), F09', u'3',
                       ['F00%', 'F01%', 'F02%', 'F03%', 'F04%', 'F05%', 'F09%', 'F06.0%', 'F06.1%', 'F06.2%', 'F06.30%', 'F06.31%', 'F06.32%', 'F06.33%', 'F06.81%', 'F06.91%'],
                       '',
                       ''],
                     [u'    из них: сосудистая деменция', u'F01', u'4',
                       ['F01%'],
                       '',
                       ''],
                     [u'    другие формы старческого слабоумия', u'F00, F02.0, F02.1-.3, F03', u'5',
                       ['F00%', 'F01%', 'F02%', 'F03%', 'F02.0%', 'F02.1%', 'F02.2%', 'F02.3%'],
                       '',
                       ''],
                     [u'    психозы и (или) слабоумие вследствие эпилепсии', u'F02.8x2, F04.2, F05.x2, F06(часть)', u'6',
                       ['F02.802%', 'F02.812%', 'F02.822%', 'F02.832%', 'F02.842%', 'F04.2%', 'F05.02%', 'F05.12%', 'F05.82%', 'F05.92%', 'F06.02%', 'F06.12%', 'F06.22%', 'F06.302%', 'F06.312%', 'F06.322%', 'F06.332%', 'F06.812%', 'F06.912%'],
                       '',
                       ''],
                     [u'  шизофрения', u'F20', u'7',
                       ['F20%'],
                       '',
                       ''],
                     [u'  шизотипические расстройства', u'F21', u'8',
                       ['F21%'],
                       '',
                       ''],
                     [u'  шизоаффективные психозы, аффективные психозы с неконгруэнтным аффекту бредом', u'F25, F3x.x4', u'9',
                       ['F25%', 'F30.24%', 'F31.24%', 'F31.54%', 'F32.34%', 'F33.34%'],
                       '',
                       ''],
                     [u'  острые и преходящие неорганические психозы', u'F23, F24', u'10',
                       ['F23%', 'F24%'],
                       '',
                       ''],
                     [u'  хронические неорганические психозы, детские психозы, неуточнённые психотические расстройства', u'F22, F28, F29, F80.31, F84.0-.4, F99.1', u'11',
                       ['F22%', 'F28%', 'F29%', 'F80.31%', 'F84.0%', 'F84.1%', 'F84.2%', 'F84.3%', 'F84.4%', 'F99.1%'],
                       '',
                       ''],
                     [u'    из них: детский аутизм, атипичный аутизм', u'F84.0-1', u'12',
                       ['F84.0%', 'F84.1%'],
                       '',
                       ''],
                     [u'  аффективные психозы', u'F30-F39(часть)', u'13',
                       ['F30.23%', 'F30.24%', 'F30.25%', 'F30.26%', 'F30.27%', 'F30.28%', 'F31.23%', 'F31.24%', 'F31.25%', 'F31.26%', 'F31.27%', 'F31.28%', 'F31.53%', 'F31.54%', 'F31.55%', 'F31.56%', 'F31.57%', 'F31.58%', 'F32.33%', 'F32.34%', 'F32.35%', 'F32.36%', 'F32.37%', 'F32.38%', 'F33.33%', 'F33.34%', 'F33.35%', 'F33.36%', 'F33.37%', 'F33.38%'],
                       '',
                       ''],
                     [u'    из них: биполярные расстройства', u'F31.23, F31.28, F31.53, F31.58', u'14',
                       ['F31.23%', 'F31.28%', 'F31.53%', 'F31.58%'],
                       '',
                       ''],
                     [u'Психические расстройства непсихотического характера', u'F06(часть), F07, F30-F38, F40-F48, F50-F69, F80.0-.2, F80.32-F83, F84.5-F89, F90-F98, F99.2-.9', u'15',
                       ['F06.4%', 'F06.5%', 'F06.6%', 'F06.7%', 'F06.34%', 'F06.35%', 'F06.36%', 'F06.37%', 'F06.82%', 'F06.92%', 'F07%', 'F30%', 'F31%', 'F32%', 'F33%', 'F34%', 'F35%', 'F36%', 'F37%', 'F38%', 'F40%', 'F41%', 'F42%', 'F43%', 'F44%', 'F45%', 'F46%', 'F47%', 'F48%', 'F50%', 'F51%', 'F52%', 'F53%', 'F54%', 'F55%', 'F56%', 'F57%', 'F58%', 'F59%', 'F60%', 'F61%', 'F62%', 'F63%', 'F64%', 'F65%', 'F66%', 'F67%', 'F68%', 'F69%', 'F81%', 'F82%', 'F83%', 'F85%', 'F86%', 'F87%', 'F88%', 'F89%', 'F90%', 'F91%', 'F92%', 'F93%', 'F94%', 'F95%', 'F96%', 'F97%', 'F98%', 'F80.0%', 'F80.1%', 'F80.2%', 'F80.32%', 'F80.33%', 'F80.34%', 'F80.35%', 'F80.36%', 'F80.37%', 'F80.38%', 'F80.39%', 'F80.4%', 'F80.5%', 'F80.6%', 'F80.7%', 'F80.8%', 'F80.9%', 'F84.5%', 'F84.6%', 'F84.7%', 'F84.8%', 'F84.9%', 'F99.2%', 'F99.3%', 'F99.4%', 'F99.5%', 'F99.6%', 'F99.7%', 'F99.8%', 'F99.9%'],
                       '',
                       ''],
                     [u'  в том числе:\nорганические непсихотические расстройства', u'F06(часть), F07', u'16',
                       ['F06.4%', 'F06.5%', 'F06.6%', 'F06.7%', 'F06.34%', 'F06.35%', 'F06.36%', 'F06.37%', 'F06.82%', 'F06.92%', 'F07%'],
                       '',
                       ''],
                     [u'    из них: обусловленные эпилепсией', u'F06(часть), F07.x2', u'17',
                       ['F06.42%', 'F06.52%', 'F06.62%', 'F06.72%', 'F06.342%', 'F06.352%', 'F06.362%', 'F06.372%', 'F06.822%', 'F06.922%', 'F06.992%', 'F07.02%', 'F07.82%', 'F07.92%'],
                       '',
                       ''],
                     [u'  аффективные непсихотические расстройства', u'F30-F38', u'18',
                       ['F30.0%', 'F30.1%', 'F31.0%', 'F31.1%', 'F30.8%', 'F30.90%', 'F30.91%', 'F30.92%', 'F30.93%', 'F30.94%', 'F31.3%', 'F31.4%', 'F31.6%', 'F31.7%', 'F31.8%', 'F31.9%', 'F32.0%', 'F32.1%', 'F32.2%', 'F32.8%', 'F32.9%', 'F33.0%', 'F33.1%', 'F33.2%', 'F33.4%', 'F33.5%', 'F33.6%', 'F33.7%', 'F33.8%', 'F33.9%', 'F35%', 'F36%', 'F37%', 'F38.0%', 'F38.1%', 'F38.2%', 'F38.3%', 'F38.4%', 'F38.5%', 'F38.6%', 'F38.7%', 'F38.8%'],
                       '',
                       ''],
                     [u'    из них: биполярные расстройства', u'F31.0, F31.1, F31.3, F31.4, F31.6-F31.9', u'19',
                       ['F31.0%', 'F31.1%', 'F31.3%', 'F31.4%', 'F31.6%', 'F31.7%', 'F31.8%', 'F31.9%'],
                       '',
                       ''],
                     [u'  невротические, связанные со стрессом и соматоформные расстройства', u'F40-F48', u'20',
                       ['F40%', 'F41%', 'F42%', 'F43%', 'F44%', 'F45%', 'F46%', 'F47%', 'F48%'],
                       '',
                       ''],
                     [u'  другие непсихотические расстройства, поведенческие расстройства детского и подросткового возраста, неуточнённые непсихотические расстройства', u'F50-F59, F80.0-.2, F80.32-F83, F84.5-F89, F90-F98, F99.2-.9', u'21',
                       ['F50%', 'F51%', 'F52%', 'F53%', 'F54%', 'F55%', 'F56%', 'F57%', 'F58%', 'F59%', 'F60%', 'F61%', 'F62%', 'F63%', 'F64%', 'F65%', 'F66%', 'F67%', 'F68%', 'F69%', 'F81%', 'F82%', 'F83%', 'F85%', 'F86%', 'F87%', 'F88%', 'F89%', 'F90%', 'F91%', 'F92%', 'F93%', 'F94%', 'F95%', 'F96%', 'F97%', 'F98%', 'F80.0%', 'F80.1%', 'F80.2%', 'F80.32%', 'F80.33%', 'F80.34%', 'F80.35%', 'F80.36%', 'F80.37%', 'F80.38%', 'F80.39%', 'F80.4%', 'F80.5%', 'F80.6%', 'F80.7%', 'F80.8%', 'F80.9%', 'F84.5%', 'F84.6%', 'F84.7%', 'F84.8%', 'F84.9%', 'F99.2%', 'F99.3%', 'F99.4%', 'F99.5%', 'F99.6%', 'F99.7%', 'F99.8%', 'F99.9%'],
                       '',
                       ''],
                     [u'    из них: синдром Аспергера', u'F84.5', u'22',
                       ['F84.5%'],
                       '',
                       ''],
                     [u'  расстройства зрелой личности и поведения у взрослых', u'F60-F69', u'23',
                       ['F60%', 'F61%', 'F62%', 'F63%', 'F64%', 'F65%', 'F66%', 'F67%', 'F68%', 'F69%'],
                       '',
                       ''],
                     [u'Умственная отсталость (всего)', u'F70-F79', u'24',
                       ['F70%', 'F71%', 'F72%', 'F73%', 'F74%', 'F75%', 'F76%', 'F77%', 'F78%', 'F79%'],
                       '',
                       ''],
                     [u'  из неё: лёгкая умственная отсталость', u'F70', u'25',
                       ['F70%'],
                       '',
                       '']]
                     # [u'Психические расстройства, классифицированные в других рубриках МКБ-10', u'G10-G40(часть)', u'24',
                     #   ['G10%', 'G20%', 'G30%', 'G31%', 'G35%', 'G40%'],
                     #   u'''LEFT JOIN Diagnosis AS diagAccompanying ON diagAccompanying.client_id = Client.id
                     #                                              AND diagAccompanying.deleted = 0
                     #                                              AND diagAccompanying.MKB LIKE 'F02.0%' AND diagAccompanying.MKB LIKE 'F02.2%' AND diagAccompanying.MKB LIKE 'F02.3%'
                     #                                              AND diagAccompanying.MKB LIKE 'F02.8_7%'
                     #                                              AND diagAccompanying.MKB LIKE 'F00.0%' AND diagAccompanying.MKB LIKE 'F00.1%' AND diagAccompanying.MKB LIKE 'F00.2%' AND diagAccompanying.MKB LIKE 'F00.9%'
                     #                                              AND diagAccompanying.MKB LIKE 'F02.802%' AND diagAccompanying.MKB LIKE 'F02.812%' AND diagAccompanying.MKB LIKE 'F02.822%' AND diagAccompanying.MKB LIKE 'F02.832%' AND diagAccompanying.MKB LIKE 'F02.842%'
                     #   LEFT JOIN rbDiagnosisType AS diagAccompanyingType ON diagAccompanyingType.id = diagAccompanying.diagnosisType_id
                     #   LEFT JOIN Diagnostic AS dignosticAccompanying ON dignosticAccompanying.diagnosis_id = diagAccompanying.id AND dignosticAccompanying.deleted = 0 ''',
                     #   u'''AND diagAccompanyingType.code = 9
                     #   AND dignosticAccompanying.endDate IS NULL
                     #   AND ((Diagnosis.MKB LIKE 'G10%' AND diagAccompanying.MKB LIKE 'F02.2%')
                     #   OR (Diagnosis.MKB LIKE 'G20%' AND diagAccompanying.MKB LIKE 'F02.3%')
                     #   OR (Diagnosis.MKB LIKE 'G31%' AND diagAccompanying.MKB LIKE 'F02.0%')
                     #   OR (Diagnosis.MKB LIKE 'G35%' AND diagAccompanying.MKB LIKE 'F02.8_7%')
                     #   OR (Diagnosis.MKB LIKE 'G30%' AND diagAccompanying.MKB LIKE 'F00.0%' AND diagAccompanying.MKB LIKE 'F00.1%' AND diagAccompanying.MKB LIKE 'F00.2%' AND diagAccompanying.MKB LIKE 'F00.9%')
                     #   OR (Diagnosis.MKB LIKE 'G40%' AND diagAccompanying.MKB LIKE 'F02.802%' AND diagAccompanying.MKB LIKE 'F02.812%' AND diagAccompanying.MKB LIKE 'F02.822%' AND diagAccompanying.MKB LIKE 'F02.832%' AND diagAccompanying.MKB LIKE 'F02.842%')) ''']]

        compilance = forceBool(params.get('chkCompilance'))
        if not compilance:
            rowNameSet[23][4] = ''
            rowNameSet[23][5] = ''

        tabTempList = [[u'Зарегистрировано больных в течение года',
                       u'в том числе в возрасте (из гр.4 т.2000)',
                       u'Из общего числа больных (гр.4 т.2000) наблюдаются и получают консультативно-лечебную помощь по состоянию на конец года',
                       '',
                       ''],

                      # [u'Из общего числа больных (гр.4 т.2000) - сельских жителей',
                      # u'в том числе в возрасте (из гр.14 т.2000)',
                      # u'Из общего числа больных - сельских жителей (гр.14 т.2000) наблюдаются и получают консультативно-лечебную помощь по состоянию на конец года',
                      # '',
                      # ''],

                      [u'Из общего числа больных (гр.4 т.3000) - с впервые в жизни установленным диагнозом',
                      u'в том числе в возрасте (из гр.4 т.3000)',
                      u'Из общего числа больных - с впервые в жизни установленным диагнозом (гр.4 т.3000) наблюдаются и получают консультативно-лечебную помощь по состоянию на конец года',
                      '',
                      u'''AND Diagnosis.id = (SELECT MIN(diagTemp2.id)
                                  FROM Diagnosis AS diagTemp2
                                  WHERE diagTemp2.client_id = Client.id AND diagTemp2.MKB = Diagnosis.MKB AND diagTemp2.deleted = 0)''']]

                      # [u'Из общего числа больных (гр.4 т.3000) - сельских жителей',
                      # u'в том числе в возрасте (из гр.14 т.3000)',
                      # u'Из общего числа больных - сельских жителей, с впервые в жизни установленным диагнозом (гр.14 т.3000) наблюдаются и получают консультативно-лечебную помощь по состоянию на конец года',
                      # '',
                      # u'''AND Diagnosis.id = (SELECT MIN(diagTemp2.id)
                      #             FROM Diagnosis AS diagTemp2
                      #             WHERE diagTemp2.client_id = Client.id AND diagTemp2.MKB = Diagnosis.MKB AND diagTemp2.deleted = 0)''']]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        def createTableHeader(cursor, header):
            tableColumns = [
                ( '10%', [u'Наименование', u'', u'', u'1'], CReportBase.AlignCenter),
                ( '7%', [u'Код по МКБ-10 (класс V, адаптированный для использования в РФ)', u'', u'', u'2'], CReportBase.AlignCenter),
                ( '3%', [u'№ стр.', u'', u'', u'3'], CReportBase.AlignCenter),
                ( '8%', [header[0], u'всего', u'', u'4'], CReportBase.AlignCenter),
                ( '8%', [u'', u'из них - женщин', u'', u'5'], CReportBase.AlignCenter),
                ( '8%', [u'', header[1], u'0 - 14 лет', u'6'], CReportBase.AlignCenter),
                ( '8%', [u'', u'', u'15 - 17 лет', u'7'], CReportBase.AlignCenter),
                ( '8%', [u'', u'', u'18 - 19 лет', u'8'], CReportBase.AlignCenter),
                ( '8%', [u'', u'', u'20 - 39 лет', u'9'], CReportBase.AlignCenter),
                ( '8%', [u'', u'', u'40 - 59 лет', u'10'], CReportBase.AlignCenter),
                ( '8%', [u'', u'', u'60 лет и старше', u'11'], CReportBase.AlignCenter),
                ( '8%', [header[2], u'', u'диспансерные больные', u'12'], CReportBase.AlignCenter),
                ( '8%', [u'', u'', u'консультативные больные', u'13'], CReportBase.AlignCenter)
            ]

            table = createTable(cursor, tableColumns)

            table.mergeCells(0, 0, 3, 1)
            table.mergeCells(0, 1, 3, 1)
            table.mergeCells(0, 2, 3, 1)
            table.mergeCells(0, 3, 1, 8)
            table.mergeCells(1, 3, 2, 1)
            table.mergeCells(1, 4, 2, 1)
            table.mergeCells(1, 5, 1, 6)
            table.mergeCells(0, 11, 2, 2)
            return table

        flag = 0
        for tabTemp in tabTempList:
            bf = QtGui.QTextCharFormat()
            bf.setFontWeight(QtGui.QFont.Bold)
            pf = QtGui.QTextCharFormat()

            cursor.insertBlock()
            cursor.setCharFormat(bf)
            if flag < 1:
                cursor.insertText(u'(2000)')
            else:
                cursor.insertText(u'(3000)')
            cursor.setCharFormat(pf)

            table = createTableHeader(cursor, tabTemp)

            columnQuery = [14, 17, 19, 39, 59, 60]

            for row in rowNameSet:
                i = table.addRow()
                table.setText(i, 0, row[0])
                table.setText(i, 1, row[1])
                table.setText(i, 2, row[2])
                if flag == 0 or flag == 1:
                    join = tabTemp[3]
                    if row[4] != '':
                        join += row[4]
                    where = tabTemp[4]
                    if row[5] != '':
                        where += row[5]
                    query = selectData(params, row[3], join, where)
                    self.setQueryText(forceString(query.lastQuery()))
                    if query.first():
                        record = query.record()
                        table.setText(i, 3, forceInt(record.value('countAll')))
                        table.setText(i, 4, forceInt(record.value('countAllFemale')))
                        table.setText(i, 11, forceInt(record.value('countAllD')))
                        table.setText(i, 12, forceInt(record.value('countAllK')))
                        j = 5
                        for countName in columnQuery:
                            table.setText(i, j, forceInt(record.value('count%s' % countName)))
                            j += 1
                else:
                    j = 3
                    while j < 13:
                        table.setText(i, j, u'0')
                        j += 1

            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertBlock()
            cursor.insertBlock()
            if flag == 0:
                cursor.insertBlock()

                row = [u'Психические расстройства, классифицированные в других рубриках МКБ-10', u'G10-G40(часть)', u'24',
                       ['G10%', 'G20%', 'G30%', 'G31%', 'G35%', 'G40%'],
                       u'''LEFT JOIN Diagnosis AS diagAccompanying ON diagAccompanying.client_id = Client.id
                                                                  AND diagAccompanying.deleted = 0
                                                                  AND diagAccompanying.MKB LIKE 'F02.0%' AND diagAccompanying.MKB LIKE 'F02.2%' AND diagAccompanying.MKB LIKE 'F02.3%'
                                                                  AND diagAccompanying.MKB LIKE 'F02.8_7%'
                                                                  AND diagAccompanying.MKB LIKE 'F00.0%' AND diagAccompanying.MKB LIKE 'F00.1%' AND diagAccompanying.MKB LIKE 'F00.2%' AND diagAccompanying.MKB LIKE 'F00.9%'
                                                                  AND diagAccompanying.MKB LIKE 'F02.802%' AND diagAccompanying.MKB LIKE 'F02.812%' AND diagAccompanying.MKB LIKE 'F02.822%' AND diagAccompanying.MKB LIKE 'F02.832%' AND diagAccompanying.MKB LIKE 'F02.842%'
                       LEFT JOIN rbDiagnosisType AS diagAccompanyingType ON diagAccompanyingType.id = diagAccompanying.diagnosisType_id
                       LEFT JOIN Diagnostic AS dignosticAccompanying ON dignosticAccompanying.diagnosis_id = diagAccompanying.id AND dignosticAccompanying.deleted = 0 ''',
                       u'''AND diagAccompanyingType.code = 9
                       AND dignosticAccompanying.endDate IS NULL
                       AND ((Diagnosis.MKB LIKE 'G10%' AND diagAccompanying.MKB LIKE 'F02.2%')
                       OR (Diagnosis.MKB LIKE 'G20%' AND diagAccompanying.MKB LIKE 'F02.3%')
                       OR (Diagnosis.MKB LIKE 'G31%' AND diagAccompanying.MKB LIKE 'F02.0%')
                       OR (Diagnosis.MKB LIKE 'G35%' AND diagAccompanying.MKB LIKE 'F02.8_7%')
                       OR (Diagnosis.MKB LIKE 'G30%' AND diagAccompanying.MKB LIKE 'F00.0%' AND diagAccompanying.MKB LIKE 'F00.1%' AND diagAccompanying.MKB LIKE 'F00.2%' AND diagAccompanying.MKB LIKE 'F00.9%')
                       OR (Diagnosis.MKB LIKE 'G40%' AND diagAccompanying.MKB LIKE 'F02.802%' AND diagAccompanying.MKB LIKE 'F02.812%' AND diagAccompanying.MKB LIKE 'F02.822%' AND diagAccompanying.MKB LIKE 'F02.832%' AND diagAccompanying.MKB LIKE 'F02.842%')) ''']

                join = tabTemp[3]
                if row[4] != '':
                    join += row[4]
                where = tabTemp[4]
                if row[5] != '':
                    where += row[5]
                query = selectData(params, row[3], join, where)
                if query.first():
                    record = query.record()
                    count = forceString(record.value('countAll'))
                else:
                    count = '0'

                cursor.insertText(u'(2100) Число психических расстройств, классифицированных в других рубриках МКБ-10, выявленных в отчетном году ' + count)
                cursor.insertBlock()
                cursor.insertBlock()

            flag += 1

        return doc

from Ui_ReportF10Setup import Ui_ReportF10SetupDialog

class CReportF10SetupDialog(QtGui.QDialog, Ui_ReportF10SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.chkIsRegistry.setChecked(params.get('chkIsRegistry', False))
        self.chkCompliance.setChecked(params.get('chkCompilance', True))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['chkIsRegistry'] = self.chkIsRegistry.isChecked()
        result['chkCompilance'] = self.chkCompliance.isChecked()
        return result