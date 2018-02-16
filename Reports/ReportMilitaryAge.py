
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceBool, forceRef, forceString, getVal

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportMilitaryAge import Ui_ReportMilitaryAge


def selectData(begDate, endDate, orgStructureId, attach, groupByArea, groupByYear):

    db = QtGui.qApp.db

    tableClientMonitoringKind     = db.table('rbClientMonitoringKind')
    tableClientMonitoring   = db.table('ClientMonitoring')

    cond = [tableClientMonitoring['setDate'].dateLe(begDate),
            db.joinOr([tableClientMonitoring['endDate'].dateGe(endDate), tableClientMonitoring['endDate'].isNull()])]

    if attach == 1:
        cond.append(tableClientMonitoringKind['code'].eq(u'К'))
    elif attach == 2:
        cond.append(tableClientMonitoringKind['code'].eq(u'Д'))
    else:
        cond.append(tableClientMonitoringKind['code'].inlist([u'К', u'Д']))
    if orgStructureId:
        cond.append('q1.orgStructure_id in (%s)' % orgStructureId)
    cond.append(tableClientMonitoring['deleted'].eq(0))

    stmt = u'''SELECT Client.id, Client.lastName, Client.firstName, Client.patrName,
                        Client.birthDate, age(Client.birthDate, curdate()) AS age,
                        getClientLocAddress(Client.id) AS address,
                        (SELECT GROUP_CONCAT(DISTINCT d.MKB SEPARATOR ', ')
                            FROM Diagnosis d
                            WHERE d.client_id = Client.id AND d.deleted = '0'
                            GROUP BY d.client_id) AS diagnosis,
                        if(rbClientMonitoringKind.code = 'К', 0, 1) AS attach, q1.orgStructure_id
              FROM Client INNER JOIN ClientMonitoring ON ClientMonitoring.`client_id`=Client.`id`
                          INNER JOIN rbClientMonitoringKind ON rbClientMonitoringKind.`id`=ClientMonitoring.`kind_id`
                          INNER JOIN   (SELECT client_id, orgStructure_id
                                        FROM ClientAttach
                                             INNER JOIN rbAttachType ON rbAttachType.`id`=ClientAttach.`attachType_id`
                                             LEFT JOIN OrgStructure ON OrgStructure.`id`=ClientAttach.`orgStructure_id`
                                        WHERE rbAttachType.code = 1) AS q1 ON q1.client_id = Client.id
              WHERE  (Client.`sex`=1) AND
                    (Client.`deleted`=0) AND
                    (TIMESTAMPDIFF(YEAR,Client.`birthDate`,now()) >= 18) AND (TIMESTAMPDIFF(YEAR,Client.`birthDate`,now()) <= 27) AND
                    %s  GROUP BY Client.`id` '''
    if groupByArea and groupByYear:
        stmt += u' ORDER BY q1.orgStructure_id, age, Client.lastName'
    elif groupByArea:
        stmt += u' ORDER BY q1.orgStructure_id, Client.lastName, age'
    elif groupByYear:
        stmt += u' ORDER BY age, Client.lastName, q1.orgStructure_id'
    else:
        stmt += u' ORDER BY Client.lastName, q1.orgStructure_id, age'

    query = db.query(stmt % (db.joinAnd(cond)))
    return query


class CReportMilitaryAge(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по количеству мужчин призывного возраста, состоящих на Д учёте и КЛП')

    def getSetupDialog(self, parent):
        result = CMilitaryAge(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate        = params.get('begDate', None)
        endDate        = params.get('endDate', None)
        orgStructureId = params.get('orgStructureId', None)
        attach         = params.get('attach', None)
        groupByArea    = params.get('groupByArea', False)
        groupByYear    = params.get('groupByYear', False)

        query = selectData(begDate, endDate, orgStructureId, attach, groupByArea, groupByYear)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        self.dumpParams(cursor, params)
        tableColumns = [('3%',   [u'№ п/п'], CReportBase.AlignLeft),
                        ('30%',  [u'ФИО'], CReportBase.AlignLeft),
                        ('7%',  [u'Дата рождения'], CReportBase.AlignLeft),
                        ('30%',  [u'Адрес'], CReportBase.AlignLeft),
                        ('30%',  [u'Диагноз'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        attachD, attachK = self.makeFormatTable(query, groupByArea)
        numOfClient = 1
        total_count = 0
        for key in attachD.keys():
            if groupByArea:
                if key:
                    orgStructureName = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', key, 'name'))
                else:
                    orgStructureName = '-'
                i = table.addRow()
                table.mergeCells(i, 0, 1, 5)
                i = table.addRow()
                table.setText(i, 0, orgStructureName, CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 5)
            if attach == 0 or attach == 2:
                i = table.addRow()
                table.setText(i, 0, u'Тип наблюдения Д', CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 5)
                lenlistD = len(attachD[key])
                prevYear = ''
                for row in xrange(lenlistD):
                    if groupByYear and self.client[attachD[key][row]][1][6:10] != prevYear:
                        i = table.addRow()
                        table.setText(i, 0, self.client[attachD[key][row]][1][6:10] + u' года рождения', CReportBase.TableTotal)
                        table.mergeCells(i, 0, 1, 5)
                        prevYear = self.client[attachD[key][row]][1][6:10]
                        numOfClient = 1
                    self.getClientInfo(numOfClient, attachD[key][row], table)
                    numOfClient += 1
                    total_count += 1
                i = table.addRow()
                table.setText(i, 0, u'всего по Д', CReportBase.TableTotal)
                table.setText(i, 1, lenlistD, CReportBase.TableTotal)
                table.mergeCells(i, 1, 1, 4)
                numOfClient = 1
            else:
                lenlistD = 0
            if attach == 0 or attach == 1:
                i = table.addRow()
                table.setText(i, 0, u'Тип наблюдения KЛП', CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 5)
                lenlistK = len(attachK[key])
                prevYear = ''
                for row in xrange(lenlistK):
                    if groupByYear and self.client[attachK[key][row]][1][6:10] != prevYear:
                        i = table.addRow()
                        table.setText(i, 0, self.client[attachK[key][row]][1][6:10] + u' года рождения', CReportBase.TableTotal)
                        table.mergeCells(i, 0, 1, 5)
                        prevYear = self.client[attachK[key][row]][1][6:10]
                        numOfClient = 1
                    self.getClientInfo(numOfClient, attachK[key][row], table)
                    numOfClient += 1
                    total_count += 1
                i = table.addRow()
                table.setText(i, 0, u'всего по KЛП', CReportBase.TableTotal)
                table.setText(i, 1, lenlistK, CReportBase.TableTotal)
                table.mergeCells(i, 1, 1, 4)
                numOfClient = 1
            else:
                lenlistK = 0
            if groupByArea:
                i = table.addRow()
                table.setText(i, 0, u'всего по участку ' + orgStructureName, CReportBase.TableTotal)
                table.setText(i, 1, lenlistK + lenlistD, CReportBase.TableTotal)
                table.mergeCells(i, 1, 1, 4)
        i = table.addRow()
        if i == 1:
            if attach == 0 or attach == 2:
                i = table.addRow()
                table.setText(i, 0, u'Тип наблюдения Д', CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 5)
                i = table.addRow()
                table.setText(i, 0, u'всего по Д', CReportBase.TableTotal)
                table.setText(i, 1, 0, CReportBase.TableTotal)
                table.mergeCells(i, 1, 1, 4)
            if attach == 0 or attach == 1:
                i = table.addRow()
                table.setText(i, 0, u'Тип наблюдения К', CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 5)
                i = table.addRow()
                table.setText(i, 0, u'всего по К', CReportBase.TableTotal)
                table.setText(i, 1, 0, CReportBase.TableTotal)
                table.mergeCells(i, 1, 1, 4)
            i = table.addRow()
        table.setText(i, 0, u'ВСЕГО', CReportBase.TableTotal)
        table.setText(i, 1, total_count, CReportBase.TableTotal)
        table.mergeCells(i, 1, 1, 4)
        return doc

    def getClientInfo(self, numOfClient, id, table):
        i = table.addRow()
        table.setText(i, 0, numOfClient)
        table.setText(i, 1, self.client[id][0])
        table.setText(i, 2, self.client[id][1] + '(' + self.client[id][2] + ')')
        table.setText(i, 3, self.client[id][3])
        table.setText(i, 4, self.client[id][4])

    def makeFormatTable(self, query, groupByArea):
        attachD = {}
        attachK = {}
        prevOrgStructure = ''
        attachDInOrgStructure = []
        attachKInOrgStructure = []
        self.client = {}
        #clientInfo = []
        orgStructure = None
        while query.next():
            record = query.record()
            id     = forceRef(record.value('id'))
            client = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            age = forceString(record.value('age'))
            address = forceString(record.value('address'))
            diagnosis = forceString(record.value('diagnosis'))
            attachType   = forceBool(record.value('attach'))
            orgStructure = forceRef(record.value('orgStructure_id'))
            self.client[id] = [client, birthDate, age, address, diagnosis]
            if not orgStructure:
                orgStructure = 0
            if prevOrgStructure and prevOrgStructure != orgStructure and groupByArea:
                attachD[prevOrgStructure] =  attachDInOrgStructure
                attachK[prevOrgStructure] =  attachKInOrgStructure
                attachDInOrgStructure = []
                attachKInOrgStructure = []
            if prevOrgStructure != orgStructure and groupByArea:
                prevOrgStructure = orgStructure
            if attachType:
                attachDInOrgStructure.append(id)
            else:
                attachKInOrgStructure.append(id)
        if orgStructure:
            attachD[orgStructure] = attachDInOrgStructure
        if orgStructure:
            attachK[orgStructure] = attachKInOrgStructure
        return attachD, attachK


class CMilitaryAge(QtGui.QDialog, Ui_ReportMilitaryAge):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate().currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate().currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbAttach.setCurrentIndex(params.get('attach', 0))
        self.chkGroupByArea.setChecked(params.get('groupByArea', False))
        self.chkGroupByYear.setChecked(params.get('groupByYear', False))

    def params(self):
        params = {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'attach': self.cmbAttach.currentIndex(),
            'groupByArea': self.chkGroupByArea.isChecked(),
            'groupByYear': self.chkGroupByYear.isChecked()
        }
        return params
