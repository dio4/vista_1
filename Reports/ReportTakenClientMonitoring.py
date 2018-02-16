# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                              import forceInt, forceString
from Reports.Report                             import CReport
from Reports.ReportBase                         import createTable, CReportBase

from Ui_ReportTakenClientMonitoring import Ui_ReportTakenClientMonitoring

def selectData(begDate, endDate, monitoringKind, otherMonitoringKind, flag, taken = True):
    db = QtGui.qApp.db
    tableDiagnosis            = db.table('Diagnosis')
    tableClientMonitoringKind = db.table('rbClientMonitoringKind')
    tableClientMonitoring     = db.table('ClientMonitoring')

    cond = [tableClientMonitoringKind['code'].eq('%s') % monitoringKind]
    if taken:
        additionalSelect = u''', count(DISTINCT Diagnosis.id) AS cnt
                             , count(DISTINCT ClientMonitoring.client_id) AS cntPrimary
                             , count(DISTINCT if(ClMonitoring.endDate <= ClientMonitoring.setDate, ClientMonitoring.client_id, NULL)) AS fromK
                             , count(DISTINCT otherRegionAttachType.id) as otherRegion'''
        additionalFrom = u'''\n left join ClientAttach on Diagnosis.client_id=ClientAttach.client_id
                        LEFT JOIN rbAttachType otherRegionAttachType ON otherRegionAttachType.id = ClientAttach.attachType_id AND otherRegionAttachType.code = 3'''
        cond.append(tableClientMonitoring['setDate'].dateGe(begDate))
        cond.append(tableClientMonitoring['setDate'].dateLe(endDate))
        if flag:
            additionalSelect += u''', count(DISTINCT rbClientRemarkType.id) AS registerFirst'''
            additionalFrom += u'''\n LEFT JOIN ClientRemark ON Diagnosis.client_id = ClientRemark.client_id
                                 LEFT JOIN rbClientRemarkType ON ClientRemark.remarkType_id = rbClientRemarkType.id AND rbClientRemarkType.flatCode = 'registerFirstInPND' '''
        else:
            additionalSelect += u''', count(DISTINCT rbAttachType.id) as fromArchive'''
            additionalFrom += u'''\n left join rbAttachType on ClientAttach.attachType_id=rbAttachType.id and rbAttachType.code=7  '''
    else:
        additionalSelect = u''', count(DISTINCT Diagnosis.id) AS cnt
                            , count(DISTINCT if(rbAttachType.code = 8 OR rbDetachmentReason.code = 9, ClientAttach.client_id, NULL)) AS dead
                            , count(DISTINCT if(rbDetachmentReason.code = 2, ClientAttach.client_id, NULL)) AS recovered
                            , count(DISTINCT if(rbDetachmentReason.code = 4, ClientAttach.client_id, NULL)) AS changeRegion
                            , count(DISTINCT if(rbDetachmentReason.code = 3, ClientAttach.client_id, NULL)) AS changeCity'''
        additionalFrom = u'''LEFT JOIN rbAttachType ON rbAttachType.code = 8
                            LEFT JOIN rbAttachType rbAttType ON  rbAttType.code = 7
                            LEFT JOIN ClientAttach ON Diagnosis.client_id = ClientAttach.client_id AND (ClientAttach.attachType_id = rbAttType.id OR ClientAttach.attachType_id = rbAttachType.id) AND ClientAttach.deleted = 0
                            left join rbDetachmentReason on rbAttType.id=rbDetachmentReason.attachType_id and rbDetachmentReason.code in(9,2,3,4)'''
        condDate = [tableClientMonitoring['endDate'].dateGe(begDate),
                    tableClientMonitoring['endDate'].dateLe(endDate)]
        if not flag:
            additionalSelect += u''', count(DISTINCT Event.id) cntEvent'''
            additionalFrom += u'''\n Left JOIN Event ON Event.id = (select max(Event.id)
            from Event
            INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id and Diagnostic.deleted = 0
            WHERE Event.client_id = Diagnosis.client_id AND Event.deleted = 0) AND date(Event.execDate) <= date_add(curdate(), INTERVAL -1 YEAR)'''
            cond.append(db.joinOr([db.joinAnd(condDate), tableClientMonitoring['endDate'].isNull()]))
        else:
            cond.append(db.joinAnd(condDate))
    cond.append(tableDiagnosis['deleted'].eq(0))

    stmt = u'''SELECT MKB_Tree.DiagName
                     , getMKBBlockID(MKB_Tree.DiagID) as BlockID
                     , Diagnosis.MKB
                     %s
                FROM
                    Diagnosis
                    INNER JOIN ClientMonitoring ON Diagnosis.client_id = ClientMonitoring.client_id
                    INNER JOIN rbClientMonitoringKind ON ClientMonitoring.kind_id = rbClientMonitoringKind.id
                    LEFT JOIN MKB_Tree ON Diagnosis.MKB = MKB_Tree.DiagID
                    LEFT JOIN rbClientMonitoringKind rbCMK ON rbCMK.code = '%s'
                    LEFT JOIN ClientMonitoring ClMonitoring ON Diagnosis.client_id = ClMonitoring.client_id AND ClMonitoring.endDate IS NOT NULL AND ClMonitoring.kind_id = rbCMK.id
                    %s
                WHERE
                    %s
                GROUP BY
                    Diagnosis.MKB
                ORDER BY
                    getMKBBlockID(MKB_Tree.DiagID), Diagnosis.MKB''' % (additionalSelect, otherMonitoringKind,  additionalFrom, db.joinAnd(cond))

    return db.query(stmt)


class CReportTakenClientMonitoring(CReport):
    def __init__(self, parent, monitoringKind=u'Д'):
        CReport.__init__(self, parent)
        self.monitoringKind = monitoringKind
        self.flag = (self.monitoringKind == u'Д')
        self.setTitle(u'Взято на %s учет' % self.monitoringKind)

    def getSetupDialog(self, parent):
        dialog = CTakenClientMonitoring(parent)
        dialog.setTitle(self.title())
        return dialog

    def build(self, params):

        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)

        query = selectData(begDate, endDate, self.monitoringKind, u'К' if self.flag else u'Д', self.flag)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('%2',  [u'Номер'], CReportBase.AlignLeft),
                        ('%5',  [u'Нозологическая форма'], CReportBase.AlignLeft),
                        ('%5',  [u'Код'], CReportBase.AlignLeft),
                        ('%5',  [u'Взято всего'], CReportBase.AlignLeft),
                        ('%5',  [u'Из них первичные'], CReportBase.AlignLeft),
                        ('%5',  [u'Из другого района'], CReportBase.AlignLeft),
                        ('%5',  [u'Из детского отделения'], CReportBase.AlignLeft),
                        ('%5',  [u'Перевод с К на Д' if self.flag else u'Перевод с Д на К'], CReportBase.AlignLeft),
                        ]

        if self.flag:
            tableColumns.insert(4, ('%5',  [u'Взято диспанцером'], CReportBase.AlignLeft))
            tableColumns.insert(5, ('%5',  [u'Взято больницей '], CReportBase.AlignLeft))
        else:
            tableColumns.insert(7, ('%5',  [u'из архива '], CReportBase.AlignLeft))


        table = createTable(cursor, tableColumns)

        currentBlockId = None
        number = total = 0

        while query.next():
            record = query.record()
            diagName = forceString(record.value('DiagName'))
            blockId = forceString(record.value('BlockID'))
            mkb = forceString(record.value('MKB'))
            cnt = forceInt(record.value('cnt'))
            fromK = forceInt(record.value('fromK'))
            primary = forceInt(record.value('cntPrimary'))
            registryFirst = forceInt(record.value('registerFirst'))
            archive = forceInt(record.value('archive'))
            otherRegion = forceInt(record.value('otherRegion'))

            if not blockId:
                blockId = u'диагнозы в базе данных отсутствуют'

            if not currentBlockId or currentBlockId != blockId:
                i = table.addRow()
                table.setText(i, 0, blockId, CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 10)
                currentBlockId = blockId
                number = 0
            i = table.addRow()
            number += 1
            total += 1
            table.setText(i, 0, number)
            table.setText(i, 1, diagName if diagName else u'диагноз в базе данных отсутствует')
            table.setText(i, 2, mkb)
            table.setText(i, 3, cnt)
            table.setText(i, 4, primary)
            if self.flag:
                table.setText(i, 5, registryFirst)
                table.setText(i, 6, primary - registryFirst)
            else:
                table.setText(i, 7, archive)
            table.setText(i, 7 if self.flag else 5, otherRegion)
            table.setText(i, 8 if self.flag else 6, '-')
            table.setText(i, 9 if self.flag else 8, fromK)

        i = table.addRow()
        table.setText(i, 0, u'Всего: ' + str(total), CReportBase.TableTotal)
        table.mergeCells(i, 0, 1, 10)
        return doc

class CReportTakenOffClientMonitoring(CReport):
    def __init__(self, parent, monitoringKind = u'Д'):
        CReport.__init__(self, parent)
        self.monitoringKind = monitoringKind
        self.flag = True if self.monitoringKind == u'Д' else False
        self.setTitle(u'Снято с %s учета' % self.monitoringKind)

    def getSetupDialog(self, parent):
        dialog = CTakenClientMonitoring(parent)
        dialog.setTitle(self.title())
        return dialog

    def build(self, params):

        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)

        query = selectData(begDate, endDate, self.monitoringKind, u'К' if self.flag else u'Д', self.flag, False)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('%2',  [u'Номер'], CReportBase.AlignLeft),
                        ('%5',  [u'Нозологическая форма'], CReportBase.AlignLeft),
                        ('%5',  [u'Код'], CReportBase.AlignLeft),
                        ('%5',  [u'Снято всего'], CReportBase.AlignLeft),
                        ('%5',  [u'С выздоравлением'], CReportBase.AlignLeft),
                        ('%5',  [u'Перевод в другой район'], CReportBase.AlignLeft),
                        ('%5',  [u'Перевод в ПНИ'], CReportBase.AlignLeft),
                        ('%5',  [u'Смерть'], CReportBase.AlignLeft)]
        if self.flag:
            tableColumns.insert(6,('%5',  [u'Перевод в другой город'], CReportBase.AlignLeft))
        if not self.flag:
            tableColumns.insert(5, ('%5',  [u'С прекращением обращения'], CReportBase.AlignLeft))

        table = createTable(cursor, tableColumns)

        currentBlockId = None
        number = 0

        while query.next():
            record = query.record()
            diagName = forceString(record.value('DiagName'))
            blockId = forceString(record.value('BlockID'))
            mkb = forceString(record.value('MKB'))
            cnt = forceInt(record.value('cnt'))
            dead = forceInt(record.value('dead'))
            recovered = forceInt(record.value('recovered'))
            changeRegion = forceInt(record.value('changeRegion'))
            changeCity = forceInt(record.value('changeCity'))
            cntEvent = forceInt(record.value('cntEvent'))

            if not blockId:
                blockId = u'диагнозы в базе данных отсутствуют'

            if not currentBlockId or currentBlockId != blockId:
                i = table.addRow()
                table.setText(i, 0, blockId, CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 9)
                currentBlockId = blockId
            i = table.addRow()
            number += 1
            table.setText(i, 0, number)
            table.setText(i, 1, diagName if diagName else u'диагноз в базе данных отсутствует')
            table.setText(i, 2, mkb)
            table.setText(i, 3, cnt)
            table.setText(i, 4, recovered)
            if self.flag:
                table.setText(i, 6, changeCity)
            else:
                table.setText(i, 5, cntEvent)
            table.setText(i, 5 if self.flag else 6, changeRegion)
            table.setText(i, 7, '-')
            table.setText(i, 8, dead)
        return doc


class CTakenClientMonitoring(QtGui.QDialog, Ui_ReportTakenClientMonitoring):
     def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

     def setTitle(self, title):
        self.setWindowTitle(title)

     def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

     def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        return params