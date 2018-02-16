# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils      import forceDate, forceInt, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


research = [
            u'%клинический%анализ крови%', 
            u'общий белок', 
            u'холестерин крови', 
            u'холестерин ЛПНП', 
            u'триглицериды сыворотки крови', 
            u'Креатинин крови', 
            u'Мочевая кислота', 
            u'Билирубин крови', 
            u'Амилаза крови', 
            u'сахар крови', 
            u'клинический%анализ%мочи', 
            u'%СА-125%', 
            u'%Онкомаркер%PSI%', 
            u'электрокардиография', 
            u'флюорография', 
            u'маммография', 
            u'Цитологическое исследование мазка%'
            ]

def preRequest(research):
    join = u"""
    LEFT JOIN (SELECT Action.id , Action.endDate, Action.event_id
    FROM
        Action
        LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
    WHERE 
        ActionType.name LIKE "%s") AS Act%d ON Act%d.event_id = Event.id
    """
    stmt = u''
    sel = u''
    for i,  r in enumerate(research):
        stmt += u'\n' + join%(r,  i,  i)
        sel += u', Act%d.endDate AS Act%dDate'%(i,  i) + u', Act%d.id AS Act%dId'%(i,  i)
    return  stmt,  sel

def selectData(params):
    stmt = u"""
    SELECT
    Client.lastName AS LastName, Client.firstName AS FirstName, Client.patrName AS PatrName, Client.birthDate AS BirthDate
    %s
    FROM
    Account_Item
    LEFT JOIN Event ON Event.id = Account_Item.event_id
    LEFT JOIN Client ON Client.id = Event.client_id
    LEFT JOIN ClientWork ON ClientWork.client_id = Client.id
    %s
    WHERE
    %s
    GROUP BY Client.id
    ORDER BY Client.lastName, Client.firstName
    """
    
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    
    cond = [
            tableAccountItem['deleted'].eq(0),
           ]
    
    extraJoin,  extraSels = preRequest(research)
    
    if params.get('accountItemIdList',  None) is not None:
        cond.append(tableAccountItem['id'].inlist(params['accountItemIdList']))
    
    finStmt = stmt %(extraSels,  extraJoin,  db.joinAnd(cond))
    return db.query(finStmt)


class CReportDopDisp(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Список к отчету о выполнении лабораторных исследований при проведении дополнительной диспансеризации \nработающих граждан')
        
    def build(self, description, params):
        reportRowSize = 19
        reportRow = []
        
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row = [u'']*reportRowSize
            row[0] = forceString(record.value('LastName'))+u' '+forceString(record.value('FirstName'))+u' '+forceString(record.value('PatrName'))
            row[1] = forceString(record.value('BirthDate'))
            for i in range(len(research)):
                str = 'Act%dId' %i
                if forceInt(record.value(str)) > 0:
                    str = 'Act%dDate' %i
                    row[i+2] = forceString(forceDate(record.value(str)))
                else:
                    row[i+2] = u'НЕ ТРЕБУЕТСЯ'
            reportRow.append(row)
            
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(description)
        cursor.insertBlock()
        
        tableColumns = [
            ('15%',  [u'ФИО'],  CReportBase.AlignLeft), 
            ('5%',  [u'Д.рожд.'],  CReportBase.AlignCenter), 
            ('5%',  [u'Анализ крови клинический'],  CReportBase.AlignCenter),  
            ('5%',  [u'Общий белок'],  CReportBase.AlignCenter),  
            ('5%',  [u'Холестерин крови'],  CReportBase.AlignCenter),  
            ('5%',  [u'Холестерин ЛПНП'],  CReportBase.AlignCenter),  
            ('5%',  [u'Тирлицериды сыворотки крови'],  CReportBase.AlignCenter),  
            ('4%',  [u'Креатинин крови'],  CReportBase.AlignCenter),  
            ('5%',  [u'Мочевая кислота'],  CReportBase.AlignCenter),  
            ('5%',  [u'Билирубин крови'],  CReportBase.AlignCenter),  
            ('5%',  [u'Амилаза крови'],  CReportBase.AlignCenter),  
            ('4%',  [u'Сахар крови'],  CReportBase.AlignCenter),  
            ('5%',  [u'Анализ мочи клинический'],  CReportBase.AlignCenter), 
            ('5%',  [u'Онко-маркер СА 125'],  CReportBase.AlignCenter), 
            ('5%',  [u'Онко-маркер PSI'],  CReportBase.AlignCenter), 
            ('4%',  [u'Электрокардиография'],  CReportBase.AlignCenter), 
            ('5%',  [u'Флюорография'],  CReportBase.AlignCenter), 
            ('4%',  [u'Маммография'],  CReportBase.AlignCenter), 
            ('5%',  [u'Цитология'],  CReportBase.AlignCenter)
            ]
            
        table = createTable(cursor, tableColumns)
        
        for r in reportRow:
            i = table.addRow()
            for j in range(reportRowSize):
                table.setText(i,  j,  r[j])
                
        return doc
