# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceInt, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    endDiagnosis = forceInt(params.get('endDiagnosis'))
    dataResult = {}
    stmt1 = u'''
        SELECT COUNT(DISTINCT IF(rbResult.code LIKE '105', Event.id, NULL)) AS countDeath,
        GROUP_CONCAT(DISTINCT IF(rbResult.code LIKE '105', Event.externalId, NULL)) AS countDeathExternalId,
        COUNT(DISTINCT Event.id) AS countAll1,
        GROUP_CONCAT(DISTINCT Event.externalId) AS countAll1ExternalId,
        COUNT(DISTINCT IF(rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.id, NULL)) AS countDeathPerNight1,
        GROUP_CONCAT(DISTINCT IF(rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.externalId, NULL)) AS countDeathPerNight1ExternalId
        FROM Event
        INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0 AND EventType.code LIKE '01'
        INNER JOIN Action AS actMov ON actMov.id = (SELECT actTempMov.id
                                                    FROM Action AS actTempMov
                                                    INNER JOIN mes.MES as tableMes ON tableMes.id = actTempMov.MES_id AND tableMes.deleted = 0
                                                    WHERE actTempMov.deleted = 0
                                                    AND actTempMov.id = (SELECT MAX(actTempMovLow.id)
                                                                        FROM Action AS actTempMovLow
                                                                        INNER JOIN ActionType AS atTempMov ON atTempMov.id = actTempMovLow.actionType_id AND atTempMov.deleted = 0 AND atTempMov.flatCode LIKE 'moving'
                                                                        WHERE actTempMovLow.deleted = 0 AND actTempMovLow.event_id = Event.id )
                                                    AND tableMes.code IN (291080, 291090, 291100))
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        WHERE Event.deleted = 0 AND DATE(Event.execDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s')
    ''' % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))

        # LEFT JOIN Action AS actRec ON actRec.deleted = 0 AND actRec.event_id = Event.id
        # LEFT JOIN ActionType AS atRec ON atRec.id = actRec.actionType_id AND atRec.deleted = 0 AND atRec.flatCode LIKE 'received'
        # INNER JOIN Action AS actLeav ON actLeav.deleted = 0 AND DATE(actLeav.begDate) >= DATE('%s') AND DATE(actLeav.begDate) <= DATE('%s') AND actLeav.event_id = Event.id
        # INNER JOIN ActionType AS atLeav ON atLeav.id = actLeav.actionType_id AND atLeav.deleted = 0 AND atLeav.flatCode LIKE 'leaved'

    query1 = db.query(stmt1)
    if query1.first():
        record1 = query1.record()
        dataResult['countDeath'] = forceInt(record1.value('countDeath'))
        dataResult['countDeathExternalId'] = forceString(record1.value('countDeathExternalId')).replace(',', '\n')
        dataResult['countAll1'] = forceInt(record1.value('countAll1'))
        dataResult['countAll1ExternalId'] = forceString(record1.value('countAll1ExternalId')).replace(',', '\n')
        dataResult['countDeathPerNight1'] = forceInt(record1.value('countDeathPerNight1'))
        dataResult['countDeathPerNight1ExternalId'] = forceString(record1.value('countDeathPerNight1ExternalId')).replace(',', '\n')
    else:
        dataResult['countDeath'] = 0
        dataResult['countDeathExternalId'] = ''
        dataResult['countAll1'] = 0
        dataResult['countAll1ExternalId'] = ''
        dataResult['countDeathPerNight1'] = 0
        dataResult['countDeathPerNight1ExternalId'] = ''

    if endDiagnosis == 0:
        diagnoseSource = u'''
            INNER JOIN Action AS diagnoseSource ON diagnoseSource.id = (SELECT MAX(actTempMain.id)
                                     FROM Action AS actTempMain
                                     WHERE actTempMain.deleted = 0
                                     AND actTempMain.id = (SELECT MAX(actTempMainLow.id)
                                                         FROM Action AS actTempMainLow
                                                         INNER JOIN ActionType AS atTempMain ON atTempMain.id = actTempMainLow.actionType_id AND atTempMain.deleted = 0 AND atTempMain.flatCode LIKE 'moving'
                                                         WHERE actTempMainLow.deleted = 0 AND actTempMainLow.event_id = Event.id )
                                     AND (actTempMain.MKB LIKE 'I60%%'
                                     OR actTempMain.MKB LIKE 'I61%%'
                                     OR actTempMain.MKB LIKE 'I62%%'
                                     OR actTempMain.MKB LIKE 'I63%%'
                                     OR actTempMain.MKB LIKE 'I64%%'
                                     OR actTempMain.MKB LIKE 'I65%%'
                                     OR actTempMain.MKB LIKE 'I66%%'
                                     OR actTempMain.MKB LIKE 'G45%%'))
        '''
    else:
        diagnoseSource = u'''
            INNER JOIN Diagnostic ON Diagnostic.id IN (SELECT diagnosticTemp.id
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
            INNER JOIN Diagnosis AS diagnoseSource ON diagnoseSource.id = Diagnostic.diagnosis_id
                AND diagnoseSource.deleted = 0
                AND (diagnoseSource.MKB LIKE 'I60%%'
                     OR diagnoseSource.MKB LIKE 'I61%%'
                     OR diagnoseSource.MKB LIKE 'I62%%'
                     OR diagnoseSource.MKB LIKE 'I63%%'
                     OR diagnoseSource.MKB LIKE 'I64%%'
                     OR diagnoseSource.MKB LIKE 'I65%%'
                     OR diagnoseSource.MKB LIKE 'I66%%'
                     OR diagnoseSource.MKB LIKE 'G45%%')
        '''

    stmt5 = u'''
        SELECT COUNT(DISTINCT IF(rbResult.code LIKE '105', Event.id, NULL)) AS countAllDeath,
        GROUP_CONCAT(DISTINCT IF(rbResult.code LIKE '105', Event.externalId, NULL)) AS countAllDeathExternalId,
        COUNT(DISTINCT Event.id) AS countAll5,
        GROUP_CONCAT(DISTINCT Event.externalId) AS countAll5ExternalId,
        COUNT(DISTINCT IF(diagnoseSource.MKB LIKE 'I63%%' OR diagnoseSource.MKB LIKE 'I64%%' OR diagnoseSource.MKB LIKE 'I65%%' OR diagnoseSource.MKB LIKE 'I66%%', Event.id, NULL)) AS count1,
        GROUP_CONCAT(DISTINCT IF(diagnoseSource.MKB LIKE 'I63%%' OR diagnoseSource.MKB LIKE 'I64%%' OR diagnoseSource.MKB LIKE 'I65%%' OR diagnoseSource.MKB LIKE 'I66%%', Event.externalId, NULL)) AS count1ExternalId,
        COUNT(DISTINCT IF(diagnoseSource.MKB LIKE 'I61%%' OR diagnoseSource.MKB LIKE 'I62%%', Event.id, NULL)) AS count2,
        GROUP_CONCAT(DISTINCT IF(diagnoseSource.MKB LIKE 'I61%%' OR diagnoseSource.MKB LIKE 'I62%%', Event.externalId, NULL)) AS count2ExternalId,
        COUNT(DISTINCT IF(diagnoseSource.MKB LIKE 'I60%%', Event.id, NULL)) AS count3,
        GROUP_CONCAT(DISTINCT IF(diagnoseSource.MKB LIKE 'I60%%', Event.externalId, NULL)) AS count3ExternalId,
        COUNT(DISTINCT IF((diagnoseSource.MKB LIKE 'I63%%' OR diagnoseSource.MKB LIKE 'I64%%' OR diagnoseSource.MKB LIKE 'I65%%' OR diagnoseSource.MKB LIKE 'I66%%') AND rbResult.code LIKE '105', Event.id, NULL)) AS count4,
        GROUP_CONCAT(DISTINCT IF((diagnoseSource.MKB LIKE 'I63%%' OR diagnoseSource.MKB LIKE 'I64%%' OR diagnoseSource.MKB LIKE 'I65%%' OR diagnoseSource.MKB LIKE 'I66%%') AND rbResult.code LIKE '105', Event.externalId, NULL)) AS count4ExternalId,
        COUNT(DISTINCT IF((diagnoseSource.MKB LIKE 'I61%%' OR diagnoseSource.MKB LIKE 'I62%%') AND rbResult.code LIKE '105', Event.id, NULL)) AS count5,
        GROUP_CONCAT(DISTINCT IF((diagnoseSource.MKB LIKE 'I61%%' OR diagnoseSource.MKB LIKE 'I62%%') AND rbResult.code LIKE '105', Event.externalId, NULL)) AS count5ExternalId,
        COUNT(DISTINCT IF(diagnoseSource.MKB LIKE 'I60%%' AND rbResult.code LIKE '105', Event.id, NULL)) AS count6,
        GROUP_CONCAT(DISTINCT IF(diagnoseSource.MKB LIKE 'I60%%' AND rbResult.code LIKE '105', Event.externalId, NULL)) AS count6ExternalId,
        COUNT(DISTINCT IF(rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.id, NULL)) AS countDeathPerNight2,
        GROUP_CONCAT(DISTINCT IF(rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.externalId, NULL)) AS countDeathPerNight2ExternalId,
        COUNT(DISTINCT IF((diagnoseSource.MKB LIKE 'I63%%' OR diagnoseSource.MKB LIKE 'I64%%' OR diagnoseSource.MKB LIKE 'I65%%' OR diagnoseSource.MKB LIKE 'I66%%') AND rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.id, NULL)) AS count7,
        GROUP_CONCAT(DISTINCT IF((diagnoseSource.MKB LIKE 'I63%%' OR diagnoseSource.MKB LIKE 'I64%%' OR diagnoseSource.MKB LIKE 'I65%%' OR diagnoseSource.MKB LIKE 'I66%%') AND rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.externalId, NULL)) AS count7ExternalId,
        COUNT(DISTINCT IF((diagnoseSource.MKB LIKE 'I61%%' OR diagnoseSource.MKB LIKE 'I62%%') AND rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.id, NULL)) AS count8,
        GROUP_CONCAT(DISTINCT IF((diagnoseSource.MKB LIKE 'I61%%' OR diagnoseSource.MKB LIKE 'I62%%') AND rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.externalId, NULL)) AS count8ExternalId,
        COUNT(DISTINCT IF(diagnoseSource.MKB LIKE 'I60%%' AND rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.id, NULL)) AS count9,
        GROUP_CONCAT(DISTINCT IF(diagnoseSource.MKB LIKE 'I60%%' AND rbResult.code LIKE '105' AND TIMESTAMPDIFF(HOUR, Event.setDate, Event.execDate) < 24, Event.externalId, NULL)) AS count9ExternalId
        FROM Event
        INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0 AND EventType.code LIKE '01'
        %s
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        WHERE Event.deleted = 0 AND DATE(Event.execDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s')
    ''' % (diagnoseSource, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))

        # LEFT JOIN Action AS actRec ON actRec.deleted = 0 AND actRec.event_id = Event.id
        # LEFT JOIN ActionType AS atRec ON atRec.id = actRec.actionType_id AND atRec.deleted = 0 AND atRec.flatCode LIKE 'received'
        # INNER JOIN Action AS actLeav ON actLeav.deleted = 0 AND DATE(actLeav.begDate) >= DATE('%s') AND DATE(actLeav.begDate) <= DATE('%s') AND actLeav.event_id = Event.id
        # INNER JOIN ActionType AS atLeav ON atLeav.id = actLeav.actionType_id AND atLeav.deleted = 0 AND atLeav.flatCode LIKE 'leaved'

    query5 = db.query(stmt5)
    if query5.first():
        record5 = query5.record()
        dataResult['countAllDeath'] = forceInt(record5.value('countAllDeath'))
        dataResult['countAllDeathExternalId'] = forceString(record5.value('countAllDeathExternalId')).replace(',', '\n')
        dataResult['countAll5'] = forceInt(record5.value('countAll5'))
        dataResult['countAll5ExternalId'] = forceString(record5.value('countAll5ExternalId')).replace(',', '\n')
        dataResult['count1'] = forceInt(record5.value('count1'))
        dataResult['count1ExternalId'] = forceString(record5.value('count1ExternalId')).replace(',', '\n')
        dataResult['count2'] = forceInt(record5.value('count2'))
        dataResult['count2ExternalId'] = forceString(record5.value('count2ExternalId')).replace(',', '\n')
        dataResult['count3'] = forceInt(record5.value('count3'))
        dataResult['count3ExternalId'] = forceString(record5.value('count3ExternalId')).replace(',', '\n')
        dataResult['count4'] = forceInt(record5.value('count4'))
        dataResult['count4ExternalId'] = forceString(record5.value('count4ExternalId')).replace(',', '\n')
        dataResult['count5'] = forceInt(record5.value('count5'))
        dataResult['count5ExternalId'] = forceString(record5.value('count5ExternalId')).replace(',', '\n')
        dataResult['count6'] = forceInt(record5.value('count6'))
        dataResult['count6ExternalId'] = forceString(record5.value('count6ExternalId')).replace(',', '\n')
        dataResult['countDeathPerNight2'] = forceInt(record5.value('countDeathPerNight2'))
        dataResult['countDeathPerNight2ExternalId'] = forceString(record5.value('countDeathPerNight2ExternalId')).replace(',', '\n')
        dataResult['count7'] = forceInt(record5.value('count7'))
        dataResult['count7ExternalId'] = forceString(record5.value('count7ExternalId')).replace(',', '\n')
        dataResult['count8'] = forceInt(record5.value('count8'))
        dataResult['count8ExternalId'] = forceString(record5.value('count8ExternalId')).replace(',', '\n')
        dataResult['count9'] = forceInt(record5.value('count9'))
        dataResult['count9ExternalId'] = forceString(record5.value('count9ExternalId')).replace(',', '\n')
    else:
        dataResult['countAllDeath'] = 0
        dataResult['countAllDeathExternalId'] = ''
        dataResult['countAll5'] = 0
        dataResult['countAll5ExternalId'] = ''
        dataResult['count1'] = 0
        dataResult['count1ExternalId'] = ''
        dataResult['count2'] = 0
        dataResult['count2ExternalId'] = ''
        dataResult['count3'] = 0
        dataResult['count3ExternalId'] = ''
        dataResult['count4'] = 0
        dataResult['count4ExternalId'] = ''
        dataResult['count5'] = 0
        dataResult['count5ExternalId'] = ''
        dataResult['count6'] = 0
        dataResult['count6ExternalId'] = ''
        dataResult['countDeathPerNight2'] = 0
        dataResult['countDeathPerNight2ExternalId'] = ''
        dataResult['count7'] = 0
        dataResult['count7ExternalId'] = ''
        dataResult['count8'] = 0
        dataResult['count8ExternalId'] = ''
        dataResult['count9'] = 0
        dataResult['count9ExternalId'] = ''
    return dataResult


class CReportMonitoringOIM(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Мониторинг ОИМ и ОНМК')

    def getSetupDialog(self, parent):
        result = CReportMonitoringOIMSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        result = selectData(params)
        self.resultSet = [[u'1.', u'Число умерших от ОИМ, всего', u'291080, 291090, 291100', u'Острый инфаркт миокарда неосложненный, Острый инфаркт миокарда осложненного течения', result['countDeath'], result['countDeathExternalId'], ''],
                     [u'1.1.', u'Число умерших от ОИМ на догоспитальном этапе', '', '', '', '', ''],
                     [u'1.2.', u'Число госпитализированных больных с ОИМ ', '', '', result['countAll1'], result['countAll1ExternalId'], ''],
                     [u'1.3.', u'Число больных ОИМ, умерших в стационаре', '', '', result['countDeath'], result['countDeathExternalId'], ''],
                     [u'1.3.1.', u'Из них умерло в первые 24 часа при поступлении в стационар', '', '', result['countDeathPerNight1'], result['countDeathPerNight1ExternalId'], ''],
                     [u'2.', u'Число больных ОИМ получивших тромболитическую терапию.', '', '', '', '', ''],
                     [u'3.', u'Число больных ОИМ получивщих рентгенэндоваскулярное обс. И лечение, всего', '', '', '', '', ''],
                     [u'3.1.', u'В том числе первые 90 минут от момента госпитализации', '', '', '', '', ''],
                     [u'4.', u'Кол-во выполненных сосудистых оперативных вмешательств при ОИМ.', '', '', '', '', ''],
                     [u'5.', u'Число умерших от церебрального инсульта, всего', u'I60, I61, I62, I63, I64, I65, I66, G45', u'Субарахноидальное кровоизлияние; внутримозговое кровоизлияние; другое нетравматическое внутричерепное кровоизлияние; инфаркт мозга; инсульт, не уточненный как кровоизлияние или инфаркт; закупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга; закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга; преходящие транзиторные церебральные ишемические приступы [атаки] и родственные синдромы', result['countAllDeath'], result['countAllDeathExternalId'], ''],
                     [u'5.1.', u'Число умерших от церебрального инсульта на догоспитальном этапе.', '', '', '', '', ''],
                     [u'5.2.', u'Число госпитализированных больных с ОНМК, всего', '', '', result['countAll5'], result['countAll5ExternalId'], ''],
                     [u'5.2.1.', u'C ишемическим инсультом', u'I63, I64, I65, I66', u'Инфаркт мозга; инсульт, не уточненный как кровоизлияние или инфаркт; закупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга; закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга', result['count1'], result['count1ExternalId'], ''],
                     [u'5.2.2.', u'С нетравматической внутримозговой гематомой', u'I61, I62', u'Внутримозговое кровоизлияние; другое нетравматическое внутричерепное кровоизлияние', result['count2'], result['count2ExternalId'], ''],
                     [u'5.2.3.', u'С субарахноидальным кровоизлиянием', u'I60', u'Субарахноидальное кровоизлияние', result['count3'], result['count3ExternalId'], ''],
                     [u'5.3.', u'Число больных с ОНМК, умерших в стационаре, всего', u'I60, I61, I62, I63, I64, I65, I66, G45', u'Субарахноидальное кровоизлияние; внутримозговое кровоизлияние; другое нетравматическое внутричерепное кровоизлияние; инфаркт мозга; инсульт, не уточненный как кровоизлияние или инфаркт; закупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга; закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга; преходящие транзиторные церебральные ишемические приступы [атаки] и родственные синдромы', result['countAllDeath'], result['countAllDeathExternalId'], ''],
                     [u'5.3.1.', u'С ишемическим инсультом', u'I63, I64, I65, I66', u'Инфаркт мозга; инсульт, не уточненный как кровоизлияние или инфаркт; закупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга; закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга', result['count4'], result['count4ExternalId'], ''],
                     [u'5.3.2.', u'С нетравматической внутримозговой гематомой', u'I61, I62', u'Внутримозговое кровоизлияние; другое нетравматическое внутричерепное кровоизлияние', result['count5'],result['count5ExternalId'], ''],
                     [u'5.3.3.', u'С субарахноидальным кровоизлиянием', u'I60', u'Субарахноидальное кровоизлияние', result['count6'], result['count6ExternalId'], ''],
                     [u'5.4.', u'Из них умерло в первые 24 часа, всего', u'I60, I61, I62, I63, I64, I65, I66, G45', u'Субарахноидальное кровоизлияние; внутримозговое кровоизлияние; другое нетравматическое внутричерепное кровоизлияние; инфаркт мозга; инсульт, не уточненный как кровоизлияние или инфаркт; закупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга; закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга; преходящие транзиторные церебральные ишемические приступы [атаки] и родственные синдромы', result['countDeathPerNight2'], result['countDeathPerNight2ExternalId'], ''],
                     [u'5.4.1.', u'С ишемическим инсультом', u'I63, I64, I65, I66', u'Инфаркт мозга; инсульт, не уточненный как кровоизлияние или инфаркт; закупорка и стеноз прецеребральных артерий, не приводящие к инфаркту мозга; закупорка и стеноз церебральных артерий, не приводящие к инфаркту мозга', result['count7'], result['count7ExternalId'], ''],
                     [u'5.4.2.', u'С нетравматической внутримозговой гематомой', u'I61, I62', u'Внутримозговое кровоизлияние; другое нетравматическое внутричерепное кровоизлияние', result['count8'], result['count8ExternalId'], ''],
                     [u'5.4.3.', u'С субарахноидальным кровоизлиянием', u'I60', u'Субарахноидальное кровоизлияние', result['count9'], result['count9ExternalId'], ''],
                     [u'6.', u'Число б-х с ОНМК, получивших тромболитическую терапию', '', '', '', '', ''],
                     [u'7.', u'Число б-х с ОНМК, получивших рентгенэндоваскулярное обследование и лечение', '', '', '', ''],
                     [u'8.', u'Кол-во выполненных сосудистых оперативных вмешательств при ОНМК, всего', '', '', '', '', ''],
                     [u'8.1.', u'При артерио-венозных мальформациях и аневризмах', '', '', '', '', ''],
                     [u'8.2.', u'При нетравматических внутримозговых гематомах', '', '', '', '', ''],
                     [u'8.3.', u'При реконструктивных операциях на магистральных сосудах головного мозга', '', '', '', '', ''],
                     [u'9.', u'Число б-х с ОНМК, независимых в повседневной жизни после проведенного лечения', '', '', '', '', '']]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        pf = QtGui.QTextCharFormat()

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '10%', [u''], CReportBase.AlignLeft),
            ( '20%', [u''], CReportBase.AlignCenter),
            ( '15%', [u'Код КСГ или МКБ для поиска соответствий'], CReportBase.AlignCenter),
            ( '15%', [u'Наименование'], CReportBase.AlignCenter),
            ( '15%', [u'За отчетный период'], CReportBase.AlignCenter),
            ( '10%', [u'№ ИБ'], CReportBase.AlignCenter),
            ( '15%', [u'За соответствующий период года, предшествующего отчетному'], CReportBase.AlignCenter)
        ]

        table = createTable(cursor, tableColumns)
        rowSize = 6

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(1, 2, 5, 1)
        table.mergeCells(1, 3, 5, 1)
        table.mergeCells(10, 2, 3, 1)
        table.mergeCells(10, 3, 3, 1)

        return doc

from Ui_ReportMonitoringOIMSetup import Ui_ReportMonitoringOIMSetupDialog

class CReportMonitoringOIMSetupDialog(QtGui.QDialog, Ui_ReportMonitoringOIMSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbEndDiagnosis.setCurrentIndex(params.get('endDiagnosis', 0))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['endDiagnosis'] = self.cmbEndDiagnosis.currentIndex()

        return result