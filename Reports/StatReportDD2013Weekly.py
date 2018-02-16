# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils           import getWorkEventTypeFilter, CPayStatus
from library.crbcombobox    import CRBComboBox
from library.database       import addDateInRange
from library.Utils          import forceInt, forceString, getVal
from Orgs.Utils             import getOrganisationInfo
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase


def selectFirstStageData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    db = QtGui.qApp.db
    diagnosisTypes = db.getIdList('rbDiagnosisType', 'id', 'code IN (\'1\', \'2\')')
    eventTypeId  = params.get('eventTypeId', None)

    stmt = u'''
    SELECT
        COUNT(DISTINCT Event.id) as total,
        COUNT(DISTINCT IF(rbSocStatusClass.code = 1, Event.id, NULL)) as veterans,
        COUNT(DISTINCT IF(Visit.scene_id = 4, Event.id, NULL)) as mobile,
        COUNT(DISTINCT IF(Diagnostic.healthGroup_id = 1, Event.id, NULL)) as hg1,
        COUNT(DISTINCT IF(Diagnostic.healthGroup_id IN (2, 3, 4, 5), Event.id, NULL)) as hg2,
        COUNT(DISTINCT IF(Diagnostic.healthGroup_id = 6, Event.id, NULL)) as hg3,
        COUNT(DISTINCT IF((Event.payStatus & (3 << (rbFinance.code * 2))) = (0x55555555 & (3 << (rbFinance.code * 2))) OR isEventPayed(Event.id), Event.id, NULL)) as exposed,
        COUNT(DISTINCT IF(isEventPayed(Event.id), Event.id, NULL)) as payed

    FROM Event
    INNER JOIN EventType ON EventType.id = Event.eventType_id and EventType.deleted = 0
    INNER JOIN rbEventKind ON EventType.eventKind_id = rbEventKind.id AND rbEventKind.code IN ('01', '04')
    INNER JOIN Client ON Client.id = Event.client_id and Client.deleted = 0
    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id and Diagnostic.deleted = 0 AND %s
    LEFT JOIN Visit ON Visit.event_id = Event.id and Visit.deleted = 0
    LEFT JOIN Contract ON Contract.id = Event.contract_id and Contract.deleted = 0
    LEFT JOIN rbFinance ON rbFinance.id = Contract.finance_id
    LEFT JOIN ClientSocStatus ON ClientSocStatus.client_id = Client.id and ClientSocStatus.deleted = 0
    LEFT JOIN rbSocStatusClass ON rbSocStatusClass.id = ClientSocStatus.socStatusClass_id
    WHERE Event.deleted = 0 AND %s
    '''

    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    cond = []
    addDateInRange(cond, tableEvent['execDate'] if not params.get('countUnfinished', False) else tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    return db.query(stmt % ((u'Diagnostic.diagnosisType_id IN (%s)' % (', '.join(str(d) for d in diagnosisTypes))) if diagnosisTypes else '1',
                                                                  db.joinAnd(cond)))

def selectSecondStageDataStarted(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)

    stmt = '''
    SELECT
        COUNT(DISTINCT Event.id) as started

    FROM Event
    INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
    INNER JOIN rbEventKind ON EventType.eventKind_id = rbEventKind.id AND rbEventKind.code = '01'
    INNER JOIN rbResult ON Event.result_id = rbResult.id AND rbResult.code IN ('49', '89', '90', '91')
    INNER JOIN Client ON Client.id = Event.client_id and Client.deleted = 0
    WHERE Event.deleted = 0 AND %s
    '''
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    cond = []
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    colsCond = []
    addDateInRange(colsCond, tableEvent['execDate'], begDate, endDate)
    return db.query(stmt % db.joinAnd(cond))

def selectSecondStageDataFinished(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)

    stmt = '''
    SELECT
        COUNT(DISTINCT IF(%s, Event.id, NULL)) as finished

    FROM Event
    INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
    INNER JOIN rbEventKind ON EventType.eventKind_id = rbEventKind.id AND rbEventKind.code = '02'
    INNER JOIN Client ON Client.id = Event.client_id and Client.deleted = 0
    WHERE Event.deleted = 0 AND %s
    '''
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    cond = []
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    colsCond = []
    addDateInRange(colsCond, tableEvent['execDate'], begDate, endDate)
    return db.query(stmt % (colsCond[0], db.joinAnd(cond)))

class CReportDD2013Weekly(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения об объемах производства диспансеризации за неделю')


    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        result.setPayStatusVisible(False)
        return result



    def build(self, params):
        queryFS = selectFirstStageData(params)
        queryFS.first()
        recordFS = queryFS.record()
        querySSS = selectSecondStageDataStarted(params)
        querySSS.first()
        recordSSS = querySSS.record()
        querySSF = selectSecondStageDataFinished(params)
        querySSF.first()
        recordSSF = querySSF.record()

        self.setQueryText('\n'.join([u'--- First stage query ---',
                                     forceString(queryFS.lastQuery()),
                                     u'\n\n\n',
                                     u'--- Second stage started query ---',
                                     forceString(querySSS.lastQuery()),
                                     u'\n\n\n',
                                     u'--- Second stage finished query ---',
                                     forceString(querySSF.lastQuery())
                                    ])
        )

        rowSize = 12
        reportRow = [0]*12
        reportRow[2] = forceInt(recordFS.value('total'))
        reportRow[3] = forceInt(recordFS.value('veterans'))
        reportRow[4] = forceInt(recordFS.value('mobile'))
        reportRow[5] = forceInt(recordFS.value('hg1'))
        reportRow[6] = forceInt(recordFS.value('hg2'))
        reportRow[7] = forceInt(recordFS.value('hg3'))
        reportRow[8] = forceInt(recordFS.value('exposed'))
        reportRow[9] = forceInt(recordFS.value('payed'))
        reportRow[10] = forceInt(recordSSS.value('started'))
        reportRow[11] = forceInt(recordSSF.value('finished'))

        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        orgId = QtGui.qApp.currentOrgId()
        orgInfo = getOrganisationInfo(orgId)
        if not orgInfo:
            QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
        shortName = getVal(orgInfo, 'shortName', u'не задано')


        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)


        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'\nЛПУ: ' + shortName)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '8%', [u'Число медицинских организаций, осуществляющих диспансеризацию в 2013 г.', u'всего'], CReportBase.AlignCenter),
            ( '8%', [u'', u'получили лицензии на проведение медицинских осмотров профилактических'], CReportBase.AlignCenter),
            ( '8%', [u'Число граждан, прошедших 1 этап диспансеризации', u'всего'], CReportBase.AlignRight),
            ( '8%', [u'', u'инвалиды и участники Великой Отечественной Войны'], CReportBase.AlignRight),
            ( '8%', [u'', u'с применением мобильных медицинских комплексов для диспансеризации'], CReportBase.AlignRight),
            ( '8%', [u'Распределение граждан, прошедших 1 этап диспансеризации, по группам состояния здоровья', u'1 группа (человек)'], CReportBase.AlignRight),
            ( '8%', [u'', u'2 группа (человек)'], CReportBase.AlignRight),
            ( '8%', [u'', u'3 группа (человек)'], CReportBase.AlignRight),
            ( '8%', [u'Число законченных случаев 1 этапа диспансеризации', u'представлено счетов к оплате'], CReportBase.AlignRight),
            ( '8%', [u'', u'из них оплачено'], CReportBase.AlignRight),
            ( '8%', [u'Число граждан, направленных на 2 этап диспансеризации', u''], CReportBase.AlignRight),
            ( '8%', [u'из них: завершили 2 этап диспансеризации', u''], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 8, 1, 2)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)
        i = table.addRow()
        for j in xrange(rowSize):
            table.setText(i, j, reportRow[j])
        return doc


from Ui_ReportDD2013WeeklySetup import Ui_ReportDD2013WeeklySetupDialog


class CReportDD2013WeeklySetupDialog(QtGui.QDialog, Ui_ReportDD2013WeeklySetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setPlanVisible(False)
        self.setTerTypeVisible(False)
        self.setPayStatusVisible(True)
        self.setSocStatusVisible(False)
        self.setEventTypeVisible(True)
        self.setPopulationGroupVisible(False)
        self.edtDDPlan.setValidator(QtGui.QIntValidator(self))
        self.cmbPayStatus.addItems([u'не задано'] + list(CPayStatus.names))
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)

    
    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.edtDDPlan.setText(forceString(params.get('planTotal', 0)))
        self.cmbTerType.setCurrentIndex(params.get('terType', 0))
        self.chkCountUnfinished.setChecked(params.get('countUnfinished', False))
        payStatus = params.get('payStatusCode', None)
        self.cmbPayStatus.setCurrentIndex((payStatus + 1) if payStatus is not None else 0)
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['planTotal'] = forceInt(self.edtDDPlan.text())
        result['terType'] = self.cmbTerType.currentIndex()
        result['countUnfinished'] = self.chkCountUnfinished.isChecked()
        # atronah: вычитание 1 для учета варианта "не задано", соответствующего None
        result['payStatusCode'] = (self.cmbPayStatus.currentIndex() - 1) if self.cmbPayStatus.currentIndex() != 0 \
                                                                         else None
        result['eventTypeId'] = self.cmbEventType.value()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        result['manualPopulation'] = self.cmbSource.currentIndex() > 0
        result['fillPopulation'] = self.grbPopulation.isChecked()
        result.update(self.processPopulation())
        return result
    

    def setPlanVisible(self, state):
        self.lblDDPlan.setVisible(state)
        self.edtDDPlan.setVisible(state)
        
    def setEventTypeVisible(self, state):
        self.lblEventType.setVisible(state)
        self.cmbEventType.setVisible(state)

    def setPayStatusVisible(self, visible):
        self.lblPayStatus.setVisible(visible)
        self.cmbPayStatus.setVisible(visible)

    def setTerTypeVisible(self, state):
        self.lblTerType.setVisible(state)
        self.cmbTerType.setVisible(state)

    def setSocStatusVisible(self, visible):
        self.lblSocStatusClass.setVisible(visible)
        self.cmbSocStatusClass.setVisible(visible)
        self.lblSocStatusType.setVisible(visible)
        self.cmbSocStatusType.setVisible(visible)

    def setDDPlanVisible(self, state):
        self.lblDDPlan.setVisible(state)
        self.edtDDPlan.setVisible(state)

    def setPopulationGroupVisible(self, state):
        self.grbPopulation.setVisible(state)

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id = %d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbSource_currentIndexChanged(self):
        manualTyping = self.cmbSource.currentIndex() > 0
        self.setDDPlanVisible(not manualTyping)
        self.setPopulationGroupVisible(manualTyping)

    def processPopulation(self):
        menPopulation = [forceInt(self.edtYoungMen.text()),
                         forceInt(self.edtMiddleMen.text()),
                         forceInt(self.edtOldMen.text())]
        menPopulationPlan = [forceInt(self.edtYoungMenPlan.text()),
                             forceInt(self.edtMiddleMenPlan.text()),
                             forceInt(self.edtOldMenPlan.text())]
        womenPopulation = [forceInt(self.edtYoungWomen.text()),
                           forceInt(self.edtMiddleWomen.text()),
                           forceInt(self.edtOldWomen.text())]
        womenPopulationPlan = [forceInt(self.edtYoungWomenPlan.text()),
                               forceInt(self.edtMiddleWomenPlan.text()),
                               forceInt(self.edtOldWomenPlan.text())]
        for column in (menPopulation, menPopulationPlan, womenPopulation, womenPopulationPlan):
            column.append(sum(column))
        #totalPopulation = [men + women for men, women in zip(menPopulation, womenPopulation)]
        #totalPopulationPlan = [men + women for men, women in zip(menPopulationPlan, womenPopulationPlan)]
        result = {
            'menPopulation': menPopulation,
            'menPopulationPlan': menPopulationPlan,
            'womenPopulation': womenPopulation,
            'womenPopulationPlan': womenPopulationPlan,
        }
        return result
