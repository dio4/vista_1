# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import re

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceInt, forceString
from library.database   import addDateInRange

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportVeteransSetup import Ui_ReportVeteransSetupDialog


# Удалено preRequest и selectData
# Тип события
eType = u'Углубленный м/о ветеранов ВОВ'


# Социальный статус
sStat = []


# Лабораторные методы исследования, функциональная диагностика: from ActionType
labResearch = [
            u'общий%клинический%анализ крови', 
            u'клинический%анализ%мочи',
            u'биохимический%анализ%крови', 
            u'альфафетопротеин', 
            u'%РЭА%', 
            u'%СА-125%', 
            u'%ПСА общий%', 
            u'%СА%19-9%', 
            u'цитологическое исследование мазка из цервикального канала%'
            u'%рентгенография органов грудной клетки%', 
            u'%маммография%', 
            u'%УЗИ брюшной полости и органов малого таза%', 
            u'%электрокардиография%', 
            u'%измерение внутриглазного давления%', 
            u'%определение остроты зрения%', 
            u'%офтальмоскопия глазного дна%', 
            ]


# Консультации врачей: from ActionType "Прием (осмотр, консультация) врача ... "
consults = [
           u'%Терапевт%', 
           u'%Невролог%',
           u'%Оториноларинголог%',
           u'%Офтальмолог%',
           u'%Эндокринолог%',
           u'%Акушер-гинеколог%',
           u'%Уролог%',
           u'%Травмотолог-ортопед'
           ]


# Дополнительные методы обследования: from ActionType
extraResearch = [
            u'%компьютерная%томография%', 
            u'%маммография%', 
            u'%эхокардиография%', 
            u'%Анализ мокроты%', 
            u'%Рентгенография%позвоночника%', 
            u'%Доплерография%', 
            u'%Доплерография%', 
            u'%УЗИ%щитовидной%железы%', 
            u'%ЭКГ%суточное%', 
            u'%ЭКГ%',
            u'%УЗИ %', 
            u'%ФВД%', 
            u'%Спирография%'
            ]


# Дополнительные консультации специалистов: ActionType "Прием (осмотр, консультация) врача ... "
extraConsults = [
            u'%Кардиолог%', 
            u'%Хирург%',
            u'%Гастроэнтеролог%',
            u'%Онколог%',
            u'%Ревматолог%',
            u'%Дерматолог%',
            u'%Инфекционист%'
            ]


# Наименования строк
rowHeadline = [
               u'1. Лабораторные методы исследования', 
               u'   развёрнутый клинический анализ крови', 
               u'   общий анализ мочи', 
               u'   биохимический анализ мочи', 
               u'   онкомаркеры:', 
               u'      альфафетопротеин', 
               u'      РЭА', 
               u'      СА-125*', 
               u'      ПСА общий**', 
               u'      СА-19-9', 
               u'   цитологическое исследование соскобов шейки матки и цервикального канала', 
               u'2. Функциональная диагностика', 
               u'   рентгенография органов грудной клетки', 
               u'   маммография/УЗИ молочных желез*', 
               u'   ульразвуковое исследование органов брюшной полости и органов малого таза', 
               u'   электрокардиографическое исследование', 
               u'   измерение внитриглазного давления', 
               u'   определение остроты зрения', 
               u'   офтальмоскопия глазного дна', 
               u'3. Консультации врачей', 
               u'   терапевт (врач общей практики (семейный врач), гериатр)', 
               u'   невролог', 
               u'   оториноларинголог', 
               u'   офтальмолог', 
               u'   эндокринолог', 
               u'   акушер-гинеколог*', 
               u'   уролог', 
               u'   травмотолог-ортопед', 
               u'4. Дополнительные методы обследования (по показаниям) ЭФГДС', 
               u'   КТ', 
               u'   Маммография по результатам УЗД', 
               u'   Эхокардиография', 
               u'   Анализ мокроты', 
               u'   Рентгенография позвоночника', 
               u'   Доплерография сосудов головного мозга', 
               u'   Доплерография сосудов нижних конечностей', 
               u'   УЗИ щитовидной железы', 
               u'   Суточное мониторирование ЭКГ', 
               u'   ЭКГ', 
               u'   УЗИ', 
               u'   ФЗД', 
               u'   Спирография', 
               u'5. Дополнительные консультауии специалистов (по показаниям)', 
               u'   Кардиолог', 
               u'   Хирург', 
               u'   Гастроэнтеролог', 
               u'   Онколог', 
               u'   Ревматолог', 
               u'   Дерматолог', 
               u'   Инфекционист'
               ]


# Функция возвращает номер похожего элемента из массива или, если в первом нет похожего элемента,
# то номер из второго массива увеличенный на 1000, для различимости
def findREName(stArray1, stArray2,   string):
    for n,  st in enumerate(stArray1):
        if re.search(st.replace('%',  '.*').lower(),  unicode(string.lower())):
            return n
    for n,  st in enumerate(stArray2):
        if re.search(st.replace('%',  '.*').lower(),  unicode(string.lower())):
            return (n+1000)
    return -1


def selectData(begDate, endDate,  personId,  orgStructureId,  eventTypeId):
    stmtActs = u"""
SELECT COUNT(*) AS cnt, rbSocStatusType.name AS socStatus, ActionType.name AS aType FROM Action
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN Event ON Action.event_id = Event.id
    LEFT JOIN Client ON Client.id = Event.client_id
    LEFT JOIN ClientSocStatus ON Client.id = ClientSocStatus.client_id
    LEFT JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
    LEFT JOIN Person ON Event.execPerson_id = Person.id
WHERE %s
GROUP BY rbSocStatusType.id, ActionType.id
ORDER BY rbSocStatusType.name
    """
    
    stmtViss = u"""
SELECT COUNT(*) AS cnt, rbSocStatusType.name AS socStatus,  rbSpeciality.name AS speciality FROM Visit
    LEFT JOIN Person ON Person.id = Visit.person_id
    LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
    LEFT JOIN Event ON Visit.event_id = Event.id
    LEFT JOIN Client ON Client.id = Event.client_id
    LEFT JOIN ClientSocStatus ON Client.id = ClientSocStatus.client_id
    LEFT JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
WHERE %s
GROUP BY rbSocStatusType.id, rbSpeciality.name
ORDER BY rbSocStatusType.name
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    
    cond = [tableEvent['deleted'].eq(0),
            tableEvent['client_id'].isNotNull()]
    addDateInRange(cond, tableEvent['setDate'], begDate,  endDate)

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if personId or orgStructureId:
        if personId:
            cond.append(tablePerson["id"].eq(personId))
        if orgStructureId:
            cond.append(tablePerson["orgStructure_id"].eq(orgStructureId))

    queryActs = db.query(stmtActs % (db.joinAnd(cond)))
    queryViss = db.query(stmtViss % (db.joinAnd(cond)))
    
    return queryActs,  queryViss


class CReportVeteransSetupDialog(QtGui.QDialog,  Ui_ReportVeteransSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        
    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['eventTypeId'] = self.cmbEventType.value()
        
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


class CReportVeterans(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения об углублённом диспансерном обследовании участников ВОВ')
        
    def getSetupDialog(self, parent):
        result = CReportVeteransSetupDialog(parent)
        result.setTitle(self.title())
        return result
        
    def build(self,  params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId',  None)
        eventTypeId = params.get('eventTypeId', None)
        
        db = QtGui.qApp.db
        reportData = {}
        reportRowSize = 6
        reportRow = [[1, 2, 3, 4, 5, 6]]
        for i,  h in enumerate(rowHeadline):
            reportRow.append([h] + [i+1] + [0]*(reportRowSize - 2))
        queryActs,  queryViss = selectData(begDate, endDate, personId,  orgStructureId, eventTypeId)
        queryTextParts = [forceString(queryActs.lastQuery())]
        while queryActs.next():
            record = queryActs.record()
            colNum = -1
            shift = -1
            socStatus = forceString(record.value('socStatus'))
            if u'ВОВ' in socStatus and not u'период' in socStatus :
                if u'погибших' in socStatus:
                    colNum = 4
                else:
                    colNum = 3
            elif u'Ленинград' in socStatus:
                colNum = 5
            elif u'инвалид' in socStatus.lower():
                colNum = 3
            else:
                continue
            count = forceInt(record.value('cnt'))
            actionType = forceString(record.value('aType'))
            num = findREName(labResearch,  extraResearch,  actionType)
            if num in [0,  1,  2]:
                shift = 2
            elif num in [3,  4,  5,  6,  7,  8]:
                shift = 3
            elif num in [9,  10,  11,  12,  13,  14,  15]:
                shift = 4
            elif (num-1000) in range(13):
                shift = -1000 + 30
            else:
                continue
                # TODO: разобраться с доплерографией
            if shift != -1:
                reportRow[num+shift][colNum] += count
                reportRow[num+shift][2] += count

        queryTextParts.append(forceString(queryViss.lastQuery()))
        self.setQueryText(u'\n\n'.join(queryTextParts))
        while queryViss.next():
            record = queryViss.record()
            colNum = -1
            shift = -1
            socStatus = forceString(record.value('socStatus'))
            if u'ВОВ' in socStatus and not u'период' in socStatus:
                if u'погибших' in socStatus:
                    colNum = 4
                else:
                    colNum = 3
            elif u'Ленинград' in socStatus:
                colNum = 5
            elif (u'инвалид' in socStatus.lower()):
                colNum = 3
            else:
                continue
            count = forceInt(record.value('cnt'))
            spec = forceString(record.value('speciality'))
            num = findREName(consults,  extraConsults,  spec)
            if num in range(8):
                shift = 21
                # TODO: к терапевтам добавит гериатров
            elif (num-1000) in range(7):
                shift = -1000 + 44
            else:
                continue
                
            if shift != -1:
                reportRow[num+shift][colNum] += count
                reportRow[num+shift][2] += count

# Вывод формы
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

# Таблица 2000
        tableColumns = [
            ('30%',  [u'Наименование'],  CReportBase.AlignLeft), 
            ('6%',  [u'№ строки'],  CReportBase.AlignCenter), 
            ('16%',  [u'Число проведенных исследований и консультаций врачей',  u'Всего'],  CReportBase.AlignCenter),
            ('16%',  [u''                            , u'в том числе:', u'инвалидам и ветеранам ВОВ'],  CReportBase.AlignCenter), 
            ('16%',  [u''                            , u'',                        u'супругам погибших (умерших) инвалидов и участников ВОВ'],  CReportBase.AlignCenter), 
            ('16%',  [u''                            , u'',                        u'лицам, награжденным знаком "Жителю блокадного Ленинграда"'],  CReportBase.AlignCenter)
            ]
    
        table = createTable(cursor,  tableColumns)
        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(1, 3, 1, 3)
        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(2, 5, 2, 1)
        
        for r in reportRow:
            i = table.addRow()
            for j in xrange(reportRowSize):
                table.setText(i,  j,  r[j])
                
        return doc

