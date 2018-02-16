# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter

from library.database   import addDateInRange
from library.Utils      import forceDate, forceInt, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Reports.Ui_ReportF32Setup import Ui_ReportF32SetupDialog


acts = [
        u'Лист обследования', 
        u'Индивидуальная карта'
        ]

props = [
         u'Терапевт', 
         u'Стоматолог', 
         u'ЛОР',
         u'Окулист', 
         u'RW',
         u'ВИЧ',
         u'HBsAg',
         u'HCV',
         u'Выявлено ВПР',
         u'PAPP-A',
         u'Альфа-ФП',
         u'ХГЧ',
         u'Осложнения данной беременности',
         u'Экстрагенитальные заболевания (диагноз)', 
         u'Поступила из другого учреждения', 
         u'3. Исход беременности', 
         u'Недель'
        ]

    

def preRequest(props):
    prestmt = u"""
    SELECT
       ActionPropertyType.name, ActionPropertyType.id ,ActionPropertyType. typeName
    FROM
        ActionPropertyType
    WHERE
        (%s
    """
    l = []
    for p in props:
        if p != props[-1]:
            l.append('name LIKE \"' + p + '\" OR')
        else:
            l.append('name LIKE \"' + p + '\")')
    # atronah (согласно базе смоленска, для которой это делалось): 
    # 1272 - Индивидуальная карта (code = '1', flatCode = '')
    # 1298 - Лист обследования (flatCode = 'explore_list') 
    l.append('AND (actionType_id = 1272 OR actionType_id = 1298) AND deleted = 0')
    st = '\n'.join(l)
    db = QtGui.qApp.db
    query = db.query(prestmt %st)
    tbl = []
    sels = []
    while query.next():
        record = query.record()
        id =  forceInt(record.value('id'))
        type =  forceString(record.value('typeName'))
        if type == 'Text':
            type = 'String'
        name = forceString(record.value('name'))
        index = props.index(name)
        tbl.append('LEFT JOIN (SELECT ActionProperty.id, ActionProperty.action_id FROM ActionProperty WHERE type_id = %d ) AS ActProps%d ON ActProps%d.action_id = Actions.id' %(id,  id,  id))
        tbl.append('LEFT JOIN ActionProperty_%s AS Prop%d ON Prop%d.id = ActProps%d.id' %(type, index , index, id ))
        sels.append(',Prop%d.value AS Prop%d'% (index,  index))
    
    return '\n'.join(sels), '\n'.join(tbl)


def selectData(begDate, endDate, eventTypeId,  personId,  personProfession,  ageFrom,  ageTo,  orgStructureId):
    stmt = u"""
SELECT
    Event.id AS EventId,
    Client.id AS ClientId,
    Event.eventType_id AS EventTypeId,
    DATE(Event.setDate) AS EventSetDate,
    DATE(CheckSheet.begDate) AS CheckSheetDate,
    Event.pregnancyWeek AS PregnancyWeek,
    age(Client.birthDate, Event.setDate) AS clientAge
    %s
FROM
    Event
    LEFT JOIN
        (SELECT * FROM Action WHERE actionType_id = 1298) AS CheckSheet
        ON Event.id = CheckSheet.event_id
    LEFT JOIN 
        (SELECT * FROM Action WHERE actionType_id = 1272 or actionType_id =1298) AS Actions
        ON Event.id = Actions.event_id
    %s
WHERE %s
"""
  
    
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    
    leftJoins = []
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableEvent['client_id'].isNotNull())
    addDateInRange(cond, tableEvent['setDate'], begDate,  endDate)

    if (personId or personProfession or orgStructureId):
        joinPerson = "LEFT JOIN %s ON %s" % (tablePerson.name(),  tablePerson["id"].eq(tableEvent["execPerson_id"]))
        leftJoins.append(joinPerson)
        if personId:
            cond.append(tablePerson["id"].eq(personId))
        if personProfession:
            cond.append(tablePerson["speciality_id"].eq(personProfession))
        if orgStructureId:
            cond.append(tablePerson["orgStructure_id"].eq(orgStructureId))
    if (ageFrom or ageTo):
        joinClient = "LEFT JOIN %s ON %s" % (tableClient.name(), tableClient["id"].eq(tableEvent["client_id"]))        
        leftJoins.append(joinClient)
        if ageFrom:
            cond.append("age(Client.birthDate, Event.setDate) >= %d" % ageFrom)
        if ageTo:
            cond.append("age(Client.birthDate, Event.setDate) <= %d" % ageTo)
    if eventTypeId:
        cond.append(tableEvent["eventType_id"].eq(eventTypeId))
    
    sels_str,  tbl_str = preRequest(props)
    joins = '\n'.join(leftJoins) + tbl_str
    return db.query(stmt %(sels_str,  joins,  db.joinAnd(cond)))

class CReportF32SetupDialog(QtGui.QDialog,  Ui_ReportF32SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpeciality.setTable('rbSpeciality', True)

    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        
    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        
        return result

    def setEnabledOrgStructureArea(self, value):
        self.cmbArea.setEnabled(value)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        if (self.edtBegDate.date() > self.edtEndDate.date()):
            self.edtEndDate.setDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        if (self.edtBegDate.date() > self.edtEndDate.date()):
            self.edtBegDate.setDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)
        
class CReportF32(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'КОНТИНГЕНТЫ БЕРЕМЕННЫХ, ПРОЖИВАЮЩИХ В РАЙОНЕ ОБСЛУЖИВАНИЯ УЧРЕЖДЕНИЯ')
        
    def getSetupDialog(self, parent):
        result = CReportF32SetupDialog(parent)
        result.setTitle(self.title())
        return result
        
    def findInMKB(self, strings,   MKBs):
        for s in strings:
            for m in MKBs:
                if m in s:
                    return True
                
    def build(self,  params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        ageFrom = params.get('ageFrom',  None)
        ageTo = params.get('ageTo',  None)
        specialityId = params.get('specialityId',  None)
        personId = params.get('personId',  None)
        
        db = QtGui.qApp.db
        reportData = {}
        query = selectData(begDate, endDate, eventTypeId, personId,  specialityId, ageFrom,  ageTo,  orgStructureId)
        reportRow2110Size = 8
        reportRow2110 = [0]*reportRow2110Size
        reportRow2120Size = 18
        reportRow2120 = [0]*reportRow2120Size
        reportRow2130Size = 8
        reportRow2130 = [[],  []]
        reportRow2130[0] = [0]*reportRow2130Size
        reportRow2130[1] = [0]*reportRow2130Size
        reportTable2130first = []
        reportTable2130second = []
        uniqueID = []
        physisOK = []
        biochemOK = []
        rwOK = []
        hivOK = []
        hbsagOK = []
        hcvOK = []
        detectvprOK = []
        detect3VPR = []
        clientDetectVPR = {}
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            pregWeek = forceInt(record.value('PregnancyWeek'))
            fromOut = forceString(record.value('Prop%d' %(props.index(u'Поступила из другого учреждения'))))
            complics = forceString(record.value('Prop%d'%(props.index(u'Осложнения данной беременности'))))
            extraGen = forceString(record.value('Prop%d' %(props.index(u'Экстрагенитальные заболевания (диагноз)'))))
            weeks = forceInt(record.value('Prop%d' %(props.index(u'Недель'))))
            pregFinal = forceString(record.value('Prop%d' %(props.index(u'3. Исход беременности'))))
            rw = forceString(record.value('Prop%d' %(props.index(u'RW'))))
            hiv = forceString(record.value('Prop%d' %(props.index(u'ВИЧ'))))
            hbsag = forceString(record.value('Prop%d' %(props.index(u'HBsAg'))))
            hcv = forceString(record.value('Prop%d' %(props.index(u'HCV'))))
            detectVPR = forceString(record.value('Prop%d' %(props.index(u'Выявлено ВПР'))))
            pappaa = forceString(record.value('Prop%d' %(props.index(u'PAPP-A'))))
            alphaFP = forceString(record.value('Prop%d' %(props.index(u'Альфа-ФП'))))
            physis = forceString(record.value('Prop%d' %(props.index(u'Терапевт'))))
            stoma = forceString(record.value('Prop%d' %(props.index(u'Стоматолог'))))
            ent = forceString(record.value('Prop%d' %(props.index(u'ЛОР'))))
            eye = forceString(record.value('Prop%d' %(props.index(u'Окулист'))))
            hcg = forceString(record.value('Prop%d' %(props.index(u'ХГЧ'))))
            clientId = forceInt(record.value('ClientId'))
            checkSheetDate = forceDate(record.value('CheckSheetDate'))
            eventSetDate = forceDate(record.value('EventSetDate'))
            period = eventSetDate.daysTo(checkSheetDate)/7 + pregWeek
            biochem2Checked = 0
            strings = [physis,  stoma,  ent,  eye,  complics,  extraGen]
            strings = list(set(strings))
            if pappaa != '':
                biochem2Checked += 1
            if alphaFP != '':
                biochem2Checked += 1
            if hcg != '':
                biochem2Checked +=1
#Таблица 2110
            reportRow2110[1] += 1
            
            if pregWeek < 12:
                reportRow2110[2] += 1
            if fromOut.lower() == u'да':
                reportRow2110[3] += 1
            if pregFinal != '':
                reportRow2110[4] += 1
                if pregFinal.lower() == u'аборт' and weeks <22:
                    reportRow2110[5] += 1
                if pregFinal .lower() == u'преждевременные' and weeks >= 22 and weeks <28:
                    reportRow2110[6] += 1
                if pregFinal.lower() == u'преждевременные' and weeks >= 28 and weeks <37:
                    reportRow2110[7] += 1
#Таблица 2120
            if pregFinal != '':
                if not (clientId in physisOK):
                    if physis != '':
                        reportRow2120[0] += 1
                        physisOK.append(clientId)
                        if period>12:
                            reportRow2120[1] += 1
                if not (clientId in rwOK):
                    if rw != '' :
                        rwOK.append(clientId)
                        if period<=20:
                            reportRow2120[2] += 1
                        if period > 20:
                            reportRow2120[3] += 1
                if not (clientId in hivOK):
                    if hiv != '':
                        hivOK.append(clientId)
                        reportRow2120[4] += 1
                        if hiv.lower() == u'положительный':
                            reportRow2120[5] += 1
                if not (clientId in hbsagOK):
                    if hbsag != u'':
                        hbsagOK.append(clientId)
                        reportRow2120[6] += 1
                        if hbsag.lower() == u'положительный':
                            reportRow2120[7] += 1
                if not (clientId in hcvOK):
                    if hcv != '':
                        hcvOK.append(clientId)
                        reportRow2120[8] += 1
                        if hcv.lower() == u'положительный':
                            reportRow2120[9] += 1
                        
                if clientId in clientDetectVPR.keys():
                    clientDetectVPR[clientId] += 1
                else:
                    clientDetectVPR[clientId] = 1
                    reportRow2120[14] += 1
                    if detectVPR.lower() == u'да':
                        reportRow2120[15] +=1
                if clientDetectVPR[clientId] == 3:
                    reportRow2120[10] +=1
                    if detectVPR.lower() == u'да':
                        reportRow2120[11] += 1
                if not (clientId in biochemOK):
                    if biochem2Checked >0:
                        reportRow2120[16] += 1
                        biochemOK.append(clientId)
                        if pappaa.lower() == u'да' or alphaFP.lower() == u'да' or hcg.lower() == u'да':
                            reportRow2120[17] += 1
                        if biochem2Checked >=2:
                            reportRow2120[12] += 1
                            if pappaa.lower() == u'да' or alphaFP.lower() == u'да' or hcg.lower() == u'да':
                                reportRow2120[13] += 1
                    
                '''if not (clientId in detectvprOK):
                    if detectVPR != '':
                        if clientDetect
                        detectvprOK.append(clientId)
                        reportRow2120[14] += 1
                        if detectvpr == 'Да':
                            reportRow2120[15]
                    else:
                       
                else if '''

#Таблица 2130
            reportRow2130[0][0] = reportRow2110[1]
            if self.findInMKB(strings,  ['O10', 'O11',  'O12',  'O13',  'O14',  'O15',  'O16' ]):
                reportRow2130[0][1] += 1
            if self.findInMKB(strings,  ['O11',  'O13',  'O14',  'O15']):
                reportRow2130[0][2] += 1
            if self.findInMKB(strings,  ['O22']):
                reportRow2130[0][3] += 1
            if self.findInMKB(strings,  ['O23']):
                reportRow2130[0][4] += 1
            if self.findInMKB(strings,  ['O20.0']):
                reportRow2130[0][5] += 1
            if self.findInMKB(strings,  ['O47.0']) and (period>21 and period <28):
                reportRow2130[0][6] += 1
            if self.findInMKB(strings,  ['O47.0']) and (period>=28 and period <37):
                reportRow2130[0][7] += 1
            if self.findInMKB(strings,  ['O36.0',  'O36.1']):
                reportRow2130[1][0] += 1
            if self.findInMKB(strings,  ['O36.3',  'O36.4',  'O36.5']):
                reportRow2130[1][1] += 1
            if self.findInMKB(strings,  ['O36.5']):
                reportRow2130[1][2] += 1
            if self.findInMKB(strings,  ['O24']):
                reportRow2130[1][3] += 1
            if self.findInMKB(strings,  ['O99.0']):
                reportRow2130[1][4] += 1
            if self.findInMKB(strings,  ['O99.2']):
                reportRow2130[1][5] += 1
            if self.findInMKB(strings,  ['O99.4']):
                reportRow2130[1][6] += 1
            
            reportRow2130[1][7] = reduce(lambda x,  y: x+y,  reportRow2130[0][1:] + reportRow2130[1][0:7],  0)

#Вывод формы       
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

#Таблица 2110
        table2110Columns = [
            ('4%',  [u'№'],  CReportBase.AlignCenter), 
            ('13%',  [u'В отчетном году',  u'Поступило под наблюдение консультации',  u'всего'],  CReportBase.AlignRight), 
            ('14%',  [u'',                            u'',                                                                    u'из них со сроком беременности до 12 недель'],  CReportBase.AlignRight), 
            ('14%',  [u'',                            u'Кроме того, поступили из числа наблюдавшихся другими учреждениями'],  CReportBase.AlignRight), 
            ('13%',  [u'',                            u'закончили беременность (из числа состоявших под наблюдением на начало года и поступивших под наблюдение в отчетном году)',  u'всего'],  CReportBase.AlignRight), 
            ('14%',  [u'',                            u'',            
                                                                    u'из них в сроке:',  u'до 22 недель'],  CReportBase.AlignRight), 
            ('14%',  [u'',                            u'', 
                                                                    u'',                            u'22-27 недель'],  CReportBase.AlignRight), 
            ('14%',  [u'',                            u'', 
                                                                    u'',                            u'28-37 недель (менее 259 дней)'],  CReportBase.AlignRight)
            ]
    
        table2110 = createTable(cursor,  table2110Columns)
        table2110.mergeCells(0, 0, 4, 1)
        table2110.mergeCells(0, 1, 1, 7)
        table2110.mergeCells(1, 1, 1, 2)
        table2110.mergeCells(2, 1, 2, 1)
        table2110.mergeCells(2, 2, 2, 1)
        table2110.mergeCells(1, 3, 3, 1)
        table2110.mergeCells(1, 4, 1, 4)
        table2110.mergeCells(2, 4, 2, 1)
        table2110.mergeCells(2, 5, 1, 3)
        
        i = table2110.addRow()
        for j in xrange(reportRow2110Size):
            table2110.setText(i,  j,  j+1)
        i = table2110.addRow()
        for j in xrange(reportRow2110Size):
            table2110.setText(i,  j,  reportRow2110[j])
         
#"Таблица" 2120       
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        reportString = u'''\nИз числа закончивших беременность (гр.5 табл.2110): были осмотрены терапевтом %d, из них до 12 недель беременности %d; были обследованы на сифилис в 1-й половине беременности %d, во 2-й половине беременности %d; на ВИЧ %d, из них выявлено сероположительных %d; гепатит В %d, из них выявлено сероположительных %d; гепатит С %d, из них выявлено сероположительных %d. Число женщин, которым проведено трехкратное скрининговое ультразвуковое исследование плода %d, число плодов, у которых выявлены врожденные пороки развития %d, число женщин, у которых взята проба на биохимический скрининг (не менее 2-ч сыворочных маркеров) %d, из них число женщин с выявленными отклонениями %d; число женщин, которым проведено УЗИ плода - всего %d; из них выявлено число плодов, у которых выявлены врожденные пороки развития - всего %d; число женщин, у которых взята проба на биохимический скрининг - всего %d; из них выявлено всего женщин с выявленными отклонениями %d.\n\n'''
        cursor.insertText(reportString % tuple(reportRow2120))
        cursor.movePosition(QtGui.QTextCursor.End)
        
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Заболевания и патологические состояния, предшествовавшие или возникшие во время беременности')
        cursor.movePosition(QtGui.QTextCursor.End)
#Таблица 2130
        reportTable2130first.append(
                               [u'Всего женщин', 
                               u'\tиз них с заболеваниями:\nотеки, протеинурия и гипертензивные расстройства', 
                               u'из них преэклампсия, эклампсия', 
                               u'венозные осложнения', 
                               u'болезни мочеполовой системы', 
                               u'угроза прерывания беременности в сроки до 22-х недель', 
                               u'угроза прерывания беременности в сроки 22-27 недель', 
                               u'угроза преждевременных родов в сроки 28-37 недель'])
        reportTable2130first.append([u'01',  u'02', u'03', u'04', u'05', u'06', u'07', u'08'])
        reportTable2130first.append([u'',  u'О10-ч.-O16-ч.',  u'O11, О13, О14, 15.0',  u'O22',  u'O23',  u'О20.0',  u'О47.0-часть',  u'О47.0-часть'])
        reportTable2130first.append(reportRow2130[0]) 
        reportTable2130second.append(
                               [u'резус-иммунизация и другие формы изоиммунизации', 
                               u'патологические состояния плода', 
                               u'из них плацентарная недостаточность', 
                               u'сахарный диабет', 
                               u'анемия', 
                               u'болезни щитовидной железы', 
                               u'болезни системы кровообращения', 
                               u'Всего заболеваний'])
        reportTable2130second.append([u'09',  u'10',  u'11', u'12', u'13', u'14', u'15', u'16'])
        reportTable2130second.append([u'О36.0-О36.1',  u'О36.3-О36.5',  u'О36.5-часть',  u'O24',  u'О99.0',  u'O99.2-часть',  u'О99.4',  u''])
        reportTable2130second.append(reportRow2130[1])
        table2130Columns = [
            ('54%',  [u'Наименование заболеваний'],  CReportBase.AlignCenter), 
            ('12%',  [u'№ строки'],  CReportBase.AlignCenter), 
            ('18%',  [u'Код по МКБ-10 пересмотра'],  CReportBase.AlignCenter), 
            ('16%',  [u'Число заболеваний'],  CReportBase.AlignCenter)
            ]

        table = createTable(cursor,  [('50%',  [],  CReportBase.AlignCenter), 
            ('50%',  [],  CReportBase.AlignCenter)],  0,  0,  0,  0)
        
        table2130 = []
        i = table.addRow()
        for j in range(2):
            table2130.append(table.setTable(i,  j,  table2130Columns))
        
        i1 = table2130[0].addRow()
        i2 = table2130[1].addRow()
        for j in range(4):
            table2130[0].setText(i1,  j,  j+1)
            table2130[1].setText(i2,  j,  j+1)
        
        for z in range(8):
            i1 = table2130[0].addRow()
            i2 = table2130[1].addRow()
            for j in range(4):
                table2130[0].setText(i1,  j,  reportTable2130first[j][z])
                table2130[1].setText(i2,  j,  reportTable2130second[j][z])
                
        return doc
        

