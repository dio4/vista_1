# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportTypeVisits import Ui_ReportTypeVisits


def selectData(begDate, endDate,  visitEmergency, visitDisp):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')

    cond = [tableEvent['deleted'].eq(0),
            tableEventType['code'].notlike('0'),
            tableEvent['setDate'].dateLe(endDate),
            tableEvent['setDate'].dateGe(begDate),
            tableEvent['execDate'].isNotNull()]

    if not visitDisp:
        cond.append(u'''EventType.code NOT IN ('dd2013_1', 'dd2013_2', 'ДДВет')''')
    if not visitEmergency:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'4\')))''''')


    stmt = u'''SELECT tbl.name AS speciality
                     , tbl.singleVisit
                     , tbl.finishedVisit
                     , count(tbl.singleVisit) AS single
                     , count(tbl.finishedVisit) AS finished
                     , count(if(tbl.order = 6, tbl.singleVisit, NULL)) AS singleCrash
                     , count(if(tbl.order = 6, tbl.finishedVisit, NULL)) AS finishedCrash
                     , count(if(tbl.code IS NOT NULL OR tbl.regionalCode IS NOT NULL, tbl.singleVisit, NULL)) AS singleProph
                     , count(if(tbl.code IS NOT NULL OR tbl.regionalCode IS NOT NULL, tbl.finishedVisit, NULL)) AS finishedProph
                     , count(if(age(tbl.birthDate, curdate()) <= 18, tbl.singleVisit, NULL)) singleChild
                     , count(if(age(tbl.birthDate, curdate()) <= 18, tbl.finishedVisit, NULL)) finishedChild
                     , count(if(if(tbl.sex = 1, age(tbl.birthDate, curdate()) >= 60, age(tbl.birthDate, curdate()) >= 55), tbl.singleVisit, NULL)) singlePensioner
                     , count(if(if(tbl.sex = 1, age(tbl.birthDate, curdate()) >= 60, age(tbl.birthDate, curdate()) >= 55), tbl.finishedVisit, NULL)) finishedPensioner
              FROM
                  (
                  SELECT rbSpeciality.name
                       , if(count(Visit.id) = 1, 1, NULL) AS singleVisit
                       , if(count(Visit.id) > 1, 1, NULL) AS finishedVisit
                       , Event.`order`
                       , rbResult.regionalCode
                       , rbEventTypePurpose.code
                       , Client.sex
                       , Client.birthDate
                  FROM
                    Event
                  INNER JOIN Client ON Client.id = Event.client_id
                  INNER JOIN EventType
                  ON Event.eventType_id = EventType.id
                  INNER JOIN Person
                  ON Person.id = Event.execPerson_id
                  INNER JOIN rbSpeciality
                  ON rbSpeciality.id = Person.speciality_id
                  INNER JOIN Visit
                  ON Visit.event_id = Event.id AND Visit.deleted = 0
                  LEFT JOIN rbEventTypePurpose
                  ON rbEventTypePurpose.id = EventType.purpose_id AND rbEventTypePurpose.code IN (2, 3, 8)
                  LEFT JOIN rbResult
                  ON rbResult.regionalCode IN (20, 21, 17, 23, 22, 18, 19) AND rbResult.id = Event.result_id
                  WHERE
                    %s
                  GROUP BY
                    Event.id) AS tbl
                GROUP BY
                  tbl.singleVisit
                , tbl.finishedVisit
                , speciality
                ORDER BY
                  tbl.finishedVisit,
                  tbl.singleVisit
                , speciality
            ''' % (db.joinAnd(cond))
    #print stmt
    return db.query(stmt)

class CReportTypeVisits(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Тип посещения')

    def getSetupDialog(self, parent):
        result = CTypeVisits(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        visitEmergency = params.get('visitEmergency')
        visitDisp = params.get('visitDisp')

        query = selectData(begDate, endDate,  visitEmergency, visitDisp)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('20%', [u''],                          CReportBase.AlignLeft),
                        ('15%', [u'Всего'],                     CReportBase.AlignLeft),
                        ('10%', [u'Из них профилактика'],       CReportBase.AlignLeft),
                        ('15%', [u'Из них неотложная помощь'],  CReportBase.AlignLeft),
                        ('15%', [u'Из них дети'],               CReportBase.AlignLeft),
                        ('15%', [u'Из них пенсионеры'],         CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        total = [0]*5
        prevSingle = prevFinished = None
        while query.next():
            record = query.record()
            speciality = forceString(record.value('speciality'))
            single = forceInt(record.value('single'))
            finished = forceInt(record.value('finished'))
            singleProph = forceInt(record.value('singleProph'))
            singleCrash = forceInt(record.value('singleCrash'))
            finishedProph = forceInt(record.value('finishedProph'))
            finishedCrash = forceInt(record.value('finishedCrash'))
            singleVisit = forceInt(record.value('singleVisit'))
            finishedVisit = forceInt(record.value('finishedVisit'))
            singleChild = forceInt(record.value('singleChild'))
            finishedChild = forceInt(record.value('finishedChild'))
            singlePensioner = forceInt(record.value('singlePensioner'))
            finishedPensioner = forceInt(record.value('finishedPensioner'))
            i = table.addRow()
            if singleVisit and not prevSingle:
                table.setText(i, 0, u'Разовые посещения', CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 4)
                prevSingle = singleVisit
                i = table.addRow()
            elif finishedVisit and not prevFinished:
                table.setText(i, 0, u'Законченный случай', CReportBase.TableTotal)
                prevFinished = finishedVisit
                table.mergeCells(i, 0, 1, 4)
                i = table.addRow()
            table.setText(i, 0 , speciality)
            if singleVisit:
                table.setText(i, 1, single)
                table.setText(i, 2, singleProph)
                table.setText(i, 3, singleCrash)
                table.setText(i, 4, singleChild)
                table.setText(i, 5, singlePensioner)
                total[0] += single
                total[1] += singleProph
                total[2] += singleCrash
                total[3] += singleChild
                total[4] += singlePensioner
            elif finishedVisit:
                table.setText(i, 1, finished)
                table.setText(i, 2, finishedProph)
                table.setText(i, 3, finishedCrash)
                table.setText(i, 4, finishedChild)
                table.setText(i, 5, finishedPensioner)
                total[0] += finished
                total[1] += finishedProph
                total[2] += finishedCrash
                total[3] += finishedChild
                total[4] += finishedPensioner
        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index in xrange(5):
            table.setText(i, index + 1, total[index])
        return doc

class CTypeVisits(QtGui.QDialog, Ui_ReportTypeVisits):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.chkVisitEmergency.setChecked(params.get('visitEmergency', False))
        self.chkVisitDisp.setChecked(params.get('visitDisp', False))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['visitEmergency'] = self.chkVisitEmergency.isChecked()
        params['visitDisp'] = self.chkVisitDisp.isChecked()
        return params
