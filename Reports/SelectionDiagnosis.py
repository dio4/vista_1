#-*- coding: utf-8 -*-#

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportSelectDiagnosis import Ui_ReportSelectionDiagnosis
from library.Utils import forceInt, forceString


def selectData(begDate, endDate, orgStructureId, personId, MKBFilter, MKBFrom, MKBTo):

    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')
    MKBTable = QtGui.qApp.db.table('MKB_Tree')

    cond = []
    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].le(endDate)]))
    cond.append(tableDiagnosis['endDate'].ge(begDate))

    diagnosticQuery = tableDiagnostic
    diagnosticCond = [ tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']),
                       tableDiagnostic['deleted'].eq(0)
                     ]
    if personId:
        diagnosticCond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond, limit='1'))

    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    else:
        cond.append(tableDiagnosis['MKB'].lt('Z'))

    stmt="""
    SELECT
       Diagnosis.MKB AS MKB,
       COUNT(*) AS sickCount,
       COUNT(DISTINCT Diagnosis.client_id) AS clientCount,
       sum(if(%s, 1, 0)) AS firstInPeriod,
       getMKBClassID(MKB_Tree.DiagID) as ClassID,
       (Select MKB2.DiagName From MKB_Tree as MKB2 Where MKB2.DiagID = getMKBClassID(MKB_Tree.DiagID) LIMIT 1 ) as ClassName,
       getMKBBlockID(MKB_Tree.DiagID) as BlockID,
       (Select MKB2.DiagName From MKB_Tree as MKB2 Where MKB2.DiagID = getMKBBlockID(MKB_Tree.DiagID) LIMIT 1 ) as BlockName,
       DiagName
    FROM Diagnosis LEFT JOIN MKB_Tree ON LEFT(MKB_Tree.DiagID, 5) = LEFT(Diagnosis.MKB, 5)
    WHERE Diagnosis.deleted=0 AND Diagnosis.mod_id IS NULL AND %s
    GROUP BY MKB
    ORDER BY ClassId, getMKBBlockID(MKB_Tree.DiagID), MKB
        """ % (db.joinAnd([tableDiagnosis['setDate'].le(endDate),
                                        tableDiagnosis['setDate'].ge(begDate)]),
                            db.joinAnd(cond))
    return db.query(stmt)


class CReportSelectionDiagnosis(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Подборка по диагнозам')


    def getSetupDialog(self, parent):
        result = CSelectionDiagnosis(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        MKBFilter = params.get('MKBFilter', 0)
        MKBFrom   = params.get('MKBFrom', '')
        MKBTo     = params.get('MKBTo', '')
        query = selectData(begDate, endDate, orgStructureId, personId, MKBFilter, MKBFrom, MKBTo)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        if params.get('isFilterAddress', False):
            self.dumpParamsAdress(cursor, params)
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('25%', [u'Наименование'], CReportBase.AlignLeft),
            ('5%',  [u'Код МКБ'], CReportBase.AlignLeft),
            ('10%', [u'Всего'], CReportBase.AlignRight),
            ('10%', [u'Впервые'], CReportBase.AlignRight),
            ('10%', [u'Чел'], CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)

        total = [0]*3
        blockTotal = [0]*3
        classTotal = [0]*3
        prevBlockId = ''
        prevClassId = ''
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            MKB       = forceString(record.value('MKB'))
            sickCount = forceInt(record.value('sickCount'))
            clientCount = forceInt(record.value('clientCount'))
            firstInPeriod = forceInt(record.value('firstInPeriod'))
            classId   = forceString(record.value('ClassID'))
            className = forceString(record.value('ClassName'))
            blockId   = forceString(record.value('BlockID'))
            blockName = forceString(record.value('BlockName'))
            MKBName   = forceString(record.value('DiagName'))
            if not classId:
                classId = '-'
            if not blockId:
                blockId = '-'
            if prevBlockId and prevBlockId != blockId:
                for j in xrange(3):
                    classTotal[j] += blockTotal[j]
                self.produceTotalLine(table, u'всего по блоку ' + prevBlockId, blockTotal)
                blockTotal = [0]*3
            if prevClassId and prevClassId != classId:
                self.produceTotalLine(table, u'всего по классу ' + prevClassId, classTotal)
                for j in xrange(3):
                    total[j] += classTotal[j]
                classTotal = [0]*3
            if  prevClassId != classId:
                i = table.addRow()
                table.setText(i, 0, classId + '. ' +className)
                table.mergeCells(i, 0, 1, 5)
                prevClassId = classId
            if  prevBlockId != blockId:
                i = table.addRow()
                table.setText(i, 0, blockId+ ' '+blockName)
                table.mergeCells(i, 0, 1, 5)
                prevBlockId = blockId

            i = table.addRow()
            table.setText(i, 0, MKBName)
            table.setText(i, 1, MKB)
            table.setText(i, 2, sickCount)
            table.setText(i, 3, firstInPeriod)
            table.setText(i, 4, clientCount)
            blockTotal[0] += sickCount
            blockTotal[1] += firstInPeriod
            blockTotal[2] += clientCount

        for j in xrange(3):
            total[j] += classTotal[j]
        self.produceTotalLine(table, u'всего по блоку ' + prevBlockId, blockTotal)
        self.produceTotalLine(table, u'всего по классу ' + prevClassId, classTotal)
        self.produceTotalLine(table, u'ВСЕГО', total)

        return doc

    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(3):
            table.setText(i, j+2, total[j], CReportBase.TableTotal)

class CSelectionDiagnosis(QtGui.QDialog, Ui_ReportSelectionDiagnosis):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
        result['MKBFrom']   = forceString(self.edtMKBFrom.text())
        result['MKBTo']     = forceString(self.edtMKBTo.text())
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)
