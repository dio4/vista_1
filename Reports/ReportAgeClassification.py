# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from Events.Utils        import getWorkEventTypeFilter
from Reports.Report      import CReport
from Reports.ReportBase  import *
from library.Utils       import *

def selectData(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    MKBFilter = forceInt(params.get('MKBFilter', 0))
    MKBFrom = forceString(params.get('MKBFrom', 'A00'))
    MKBTo = forceString(params.get('MKBTo', 'Z99.9'))
    personId  = forceInt(params.get('personId', 0))
    primary = forceInt(params.get('primary', 0))
    eventTypeId = forceInt(params.get('eventTypeId', None))

    join = ''
    where = ''
    if begDate:
        where += u"AND DATE(Event.execDate) >= DATE('%s') " % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += u"AND DATE(Event.execDate) <= DATE('%s') " % endDate.toString('yyyy-MM-dd')
    if MKBFilter == 1:
        join += u'''
            INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
            INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
        '''
        where += u"AND Diagnosis.MKB >= '%(from)s' AND Diagnosis.MKB <= '%(to)s' " % {'from' : MKBFrom, 'to' : MKBTo}
    if personId:
        where += u"AND Event.execPerson_id = %s " % personId
    if primary:
        where += u"AND Event.isPrimary = %s " % primary
    if eventTypeId:
        where += u"AND Event.eventType_id = %s " % eventTypeId

    stmt = u'''
        SELECT Person.lastName,
            Person.firstName,
            Person.patrName,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) < 5 AND Client.sex = 1, Client.id, NULL)) AS age05m,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) < 5 AND Client.sex = 2, Client.id, NULL)) AS age05f,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) >= 5 AND age(Client.birthDate, Event.execDate) < 18 AND Client.sex = 1, Client.id, NULL)) AS age518m,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) >= 5 AND age(Client.birthDate, Event.execDate) < 18 AND Client.sex = 2, Client.id, NULL)) AS age518f,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) >= 18 AND age(Client.birthDate, Event.execDate) < 59 AND Client.sex = 1, Client.id, NULL)) AS age1859m,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) >= 18 AND age(Client.birthDate, Event.execDate) < 54 AND Client.sex = 2, Client.id, NULL)) AS age1854f,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) >= 60 AND Client.sex = 1, Client.id, NULL)) AS age60m,
            COUNT(DISTINCT IF(age(Client.birthDate, Event.execDate) >= 55 AND Client.sex = 2, Client.id, NULL)) AS age55f,
            COUNT(DISTINCT Client.id) AS `all`
        FROM Event
        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
        INNER JOIN Person ON Person.id = Event.execPerson_id AND Person.deleted = 0
        %(join)s
        WHERE Event.deleted = 0 %(where)s
        GROUP BY Person.lastName, Person.firstName, Person.patrName
    ''' % {'where' : where,
           'join' : join}
    return db.query(stmt)


class CReportAgeClassification(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по возрастам')

    def getSetupDialog(self, parent):
        result = CReportAgeClassificationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '10%', [u'Врачи', u'', u''], CReportBase.AlignCenter),
            ( '10%', [u'Дети', u'0-4 года', u'муж'], CReportBase.AlignCenter),
            ( '10%', [u'', u'', u'жен'], CReportBase.AlignCenter),
            ( '10%', [u'', u'5-17 лет', u'муж'], CReportBase.AlignCenter),
            ( '10%', [u'', u'', u'жен'], CReportBase.AlignCenter),
            ( '10%', [u'Трудоспособный возраст', u'18-59 лет', u'муж'], CReportBase.AlignCenter),
            ( '10%', [u'', u'18-54 лет', u'жен'], CReportBase.AlignCenter),
            ( '10%', [u'Пенсионный возраст', u'60 лет и старше', u'муж'], CReportBase.AlignCenter),
            ( '10%', [u'', u'55 лет и старше', u'жен'], CReportBase.AlignCenter),
            ( '10%', [u'Всего', u'', u''], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 4)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(0, 5, 1, 2)
        table.mergeCells(0, 7, 1, 2)
        table.mergeCells(0, 9, 3, 1)

        query = selectData(params)

        sum = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName')))
            table.setText(i, 1, forceString(record.value('age05m')))
            sum[0] += forceInt(record.value('age05m'))
            table.setText(i, 2, forceString(record.value('age05f')))
            sum[1] += forceInt(record.value('age05f'))
            table.setText(i, 3, forceString(record.value('age518m')))
            sum[2] += forceInt(record.value('age518m'))
            table.setText(i, 4, forceString(record.value('age518f')))
            sum[3] += forceInt(record.value('age518f'))
            table.setText(i, 5, forceString(record.value('age1859m')))
            sum[4] += forceInt(record.value('age1859m'))
            table.setText(i, 6, forceString(record.value('age1854f')))
            sum[5] += forceInt(record.value('age1854f'))
            table.setText(i, 7, forceString(record.value('age60m')))
            sum[6] += forceInt(record.value('age60m'))
            table.setText(i, 8, forceString(record.value('age55f')))
            sum[7] += forceInt(record.value('age55f'))
            table.setText(i, 9, forceString(record.value('all')))
            sum[8] += forceInt(record.value('all'))

        i = table.addRow()
        table.setText(i, 0, u'Итого:', fontBold=True)
        for j in xrange(9):
            table.setText(i, j + 1, sum[j])

        return doc

from Ui_ReportAgeClassificationSetup import Ui_ReportAgeClassificationSetupDialog

class CReportAgeClassificationSetupDialog(QtGui.QDialog, Ui_ReportAgeClassificationSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbPrimary.setCurrentIndex(params.get('primary', 0))
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        self.cmbEventType.setValue(params.get('eventTypeId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['personId'] = self.cmbPerson.value()
        result['primary'] = self.cmbPrimary.currentIndex()
        result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
        result['MKBFrom']   = self.edtMKBFrom.text()
        result['MKBTo']     = self.edtMKBTo.text()
        result['eventTypeId'] = self.cmbEventType.value()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)