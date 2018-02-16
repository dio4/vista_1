# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceDouble, forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportSurgicalIndicators import Ui_ReportSurgicalIndicators

def selectData(params, lstSpeciality, lstOrgStructure, lstOperation):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    order = params.get('order')
    spetialityId = params.get('specialityId')
    orgStructureId = params.get('orgStructureId')
    operationId = params.get('operationId')
    typeHosp = params.get('typeHosp')
    chkSpeciality = params.get('chkSpeciality')
    cmbOperation = params.get('cmbOperation')
    cmbOrgStructure = params.get('cmbOrgStructure')
    financeId       = params.get('financeId')

    tableAction = db.table('Action').alias('a')
    tableActionOperation = db.table('Action').alias('a_operation')

    condLeaved = [tableAction['endDate'].dateGe(begDate),
                  tableAction['endDate'].dateLe(endDate)]
    condOperation = [tableActionOperation['endDate'].dateGe(begDate),
                    tableActionOperation['endDate'].dateLe(endDate)]

    if order:
        tableEvent = db.table('Event')
        condLeaved.append(tableEvent['order'].eq(order))
        condOperation.append(tableEvent['order'].eq(order))
    if typeHosp == 1:
        condOperation.append(u'OrgStructure.code = 0')
        condLeaved.append(u'OrgStructure.code = 0')
    elif typeHosp == 2:
        condOperation.append(u'OrgStructure.hasDayStationary = 1')
        condLeaved.append(u'OrgStructure.hasDayStationary = 1')
    elif typeHosp == 3:
        condOperation.append('aps_received.value IS NOT NULL')
        condLeaved.append('aps_received.value IS NOT NULL')
    if lstSpeciality and chkSpeciality:
        tablePerson = db.table('Person').alias('p')
        condOperation.append(tablePerson['speciality_id'].inlist(lstSpeciality))
        condLeaved.append(tablePerson['speciality_id'].inlist(lstSpeciality))
    if lstOrgStructure and cmbOrgStructure:
        tableOrgStructure = db.table('OrgStructure')
        condOperation.append(tableOrgStructure['id'].inlist(lstOrgStructure))
        condLeaved.append(tableOrgStructure['id'].inlist(lstOrgStructure))
    if lstOperation and cmbOperation:
        tableOperation = db.table('ActionType').alias('a_operation')
        condOperation.append(tableOperation['id'].inlist(lstOperation))
    if spetialityId and not chkSpeciality:
        tablePerson = db.table('Person').alias('p')
        condOperation.append(tablePerson['speciality_id'].eq(spetialityId))
        condLeaved.append(tablePerson['speciality_id'].eq(spetialityId))
    if orgStructureId and not cmbOrgStructure:
        tableOrgStructure = db.table('OrgStructure')
        condOperation.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
        condLeaved.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if operationId and not cmbOperation:
        tableOperation = db.table('ActionType').alias('a_operation')
        condOperation.append(tableOperation['id'].eq(operationId))
    if financeId:
        tableContract = db.table('Contract')
        condOperation.append(tableAction['finance_id'].eq(financeId))
        condLeaved.append(tableContract['finance_id'].eq(financeId))

    stmt = u'''SELECT info.code,
                      info.Person,
                      leaved.leaved,
                      operation.operation,
                      operation.operationClient,
                      operation.resultDischarged,
                      operation.resultDead,
                      operation.resultTransferred,
                      operation.resultContinued,
                      operation.resultRecovery,
                      operation.resultImprovement,
                      operation.resultDeterioration,
                      operation.resultStatic
            FROM (SELECT OrgStructure.id AS orgStructureId,
                         OrgStructure.code,
                         Person.id AS personId,
                         CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS Person
                  FROM	OrgStructure, Person) AS info
            LEFT JOIN (SELECT apos.value,
                           a_operation.person_id,
                           COUNT(DISTINCT a_operation.id) AS operation,
                           COUNT(DISTINCT e.id) AS operationClient,
                           COUNT(DISTINCT IF(r.name LIKE 'Выписан%%', e.id, NULL)) AS resultDischarged,
                           COUNT(DISTINCT IF(r.name LIKE '%%Умер%%' OR r.name LIKE 'Смерть%%', e.id, NULL)) AS resultDead,
                           COUNT(DISTINCT IF(r.name LIKE 'Переведен%%', e.id, NULL)) AS resultTransferred,
                           COUNT(DISTINCT IF(r.name = 'Лечение продолжено', e.id, NULL)) AS resultContinued,
                           COUNT(DISTINCT IF(aps.value = 'Выздоровление', e.id, NULL)) AS resultRecovery,
                           COUNT(DISTINCT IF(aps.value = 'Улучшение', e.id, NULL)) AS resultImprovement,
                           COUNT(DISTINCT IF(aps.value = 'Ухудшение', e.id, NULL)) AS resultDeterioration,
                           COUNT(DISTINCT IF(aps.value = 'Без перемен', e.id, NULL)) AS resultStatic
                     FROM Event e
                           INNER JOIN Action a ON a.event_id = e.id AND a.deleted = 0
                           INNER JOIN ActionType AT ON AT.id = a.actionType_id
                           INNER JOIN Action a_operation ON a_operation.event_id = e.id AND a_operation.deleted = 0
                           INNER JOIN ActionType at_operation   ON at_operation.id = a_operation.actionType_id AND at_operation.serviceType = 4
                           INNER JOIN Action a_moving ON a_moving.event_id = e.id AND a_moving.actionType_id = (SELECT ActionType.id
                                                                                                                FROM ActionType
                                                                                                                WHERE ActionType.flatCode = 'moving') AND a_moving.begDate <= a_operation.begDate
                                                                                                                        AND a_moving.endDate >= a_operation.endDate
                                                                                                                        AND a_moving.deleted = 0
                           LEFT JOIN ActionPropertyType apt_moving ON apt_moving.actionType_id = a_moving.actionType_id AND apt_moving.name = 'Отделение пребывания'
                           LEFT JOIN ActionProperty ap_moving ON ap_moving.action_id = a_moving.id AND ap_moving.type_id = apt_moving.id AND ap_moving.deleted = 0
                           LEFT JOIN ActionProperty_OrgStructure apos ON apos.id = ap_moving.id
                           LEFT JOIN OrgStructure ON OrgStructure.id = apos.value
                           LEFT JOIN ActionPropertyType apt_result  ON apt_result.actionType_id = a_moving.actionType_id AND apt_result.name = 'Результат'
                           LEFT JOIN ActionProperty ap_result ON ap_result.action_id = a_moving.id AND ap_result.type_id = apt_result.id AND ap_result.deleted = 0
                           LEFT JOIN ActionProperty_String aps  ON aps.id = ap_result.id
                           LEFT JOIN Action a_received ON a_received.event_id = e.id AND a_received.deleted = 0
                           LEFT JOIN ActionType at_received ON at_received.id = a_received.actionType_id AND at_received.flatCode = 'received'
                           LEFT JOIN ActionPropertyType apt_received ON apt_received.actionType_id = at_received.id AND apt_received.name = 'Причина отказа от госпитализации'
                           LEFT JOIN ActionProperty ap_received ON ap_received.action_id = a_received.id AND ap_received.type_id = apt_received.id AND ap_received.deleted = 0
                           LEFT JOIN ActionProperty_String aps_received ON aps_received.id = ap_received.id
                           LEFT JOIN rbResult r ON r.id = e.result_id
                           INNER JOIN Person p ON p.id = a_operation.person_id
                     WHERE %s AND AT.flatCode = 'leaved' AND e.deleted = 0
                     GROUP BY	apos.value, a_operation.person_id) operation ON operation.value = info.orgStructureId AND info.personId = operation.person_id
            LEFT JOIN (SELECT   apos.value,
                                e.execPerson_id,
                                COUNT(DISTINCT a.id) AS leaved
                        FROM Event e
                            INNER JOIN Person p ON p.id = e.execPerson_id
                            INNER JOIN Action a ON a.event_id = e.id AND a.deleted = 0
                            INNER JOIN ActionType at ON at.id = a.actionType_id
                            INNER JOIN Action a_moving  ON a_moving.event_id = e.id AND a_moving.id = (SELECT MAX(Action.id)
                                                                                                       FROM Action
                                                                                                        INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                                                                                                        WHERE ActionType.flatCode = 'moving' AND Action.event_id = e.id AND Action.deleted = 0)
                            INNER JOIN ActionPropertyType apt_moving ON apt_moving.actionType_id = a_moving.actionType_id AND apt_moving.name = 'Отделение пребывания'
                            INNER JOIN ActionProperty ap_moving ON ap_moving.action_id = a_moving.id AND ap_moving.type_id = apt_moving.id AND ap_moving.deleted = 0
                            INNER JOIN ActionProperty_OrgStructure apos ON apos.id = ap_moving.id
                            LEFT JOIN OrgStructure ON OrgStructure.id = apos.value
                            LEFT JOIN Action a_received ON a_received.event_id = e.id AND a_received.deleted = 0
                            LEFT JOIN ActionType at_received ON at_received.id = a_received.actionType_id AND at_received.flatCode = 'received'
                            LEFT JOIN ActionPropertyType apt_received ON apt_received.actionType_id = at_received.id AND apt_received.name = 'Причина отказа от госпитализации'
                            LEFT JOIN ActionProperty ap_received ON ap_received.action_id = a_received.id AND ap_received.type_id = apt_received.id AND ap_received.deleted = 0
                            LEFT JOIN ActionProperty_String aps_received ON aps_received.id = ap_received.id
                            LEFT JOIN OrgStructure os   ON os.id = apos.value
                            LEFT JOIN Contract ON Contract.id = e.contract_id
                        WHERE at.flatCode = 'leaved' AND %s AND e.deleted = 0
                        GROUP BY	os.id, p.id) leaved ON leaved.value = info.orgStructureId AND leaved.execPerson_id = info.personId

            WHERE operation.operation IS NOT NULL OR leaved.leaved IS NOT NULL
            GROUP BY code, Person
            ORDER BY code, Person''' % (db.joinAnd(condOperation), db.joinAnd(condLeaved))
    return db.query(stmt)

class CReportSurgicalIndicators(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Некоторые показатели работы хирурга (без учета абортов)')

    def getSetupDialog(self, parent):
        result = CSurgicalIndicators(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        lstOperationDict = params.get('lstOperation', None)
        lstOperation = lstOperationDict.keys()
        lstSpecialityDict = params.get('lstSpeciality', None)
        lstSpeciality = lstSpecialityDict.keys()
        query = selectData(params, lstSpeciality, lstOrgStructure, lstOperation)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '10%', [u'Отделение'                      ], CReportBase.AlignLeft),
            ( '20%', [u'ФИО'                            ], CReportBase.AlignRight),
            ( ' 5%', [u'Количество выбывших'            ], CReportBase.AlignLeft),
            ( ' 5%', [u'Оперировано (количество выбывших)'], CReportBase.AlignLeft),
            ( ' 5%', [u'Количество операций'], CReportBase.AlignLeft),
            ( ' 5%', [u'Хир. актив %'                   ], CReportBase.AlignLeft),
            ( ' 5%', [u'Имели осложнен.'                ], CReportBase.AlignLeft),
            ( ' 5%', [u'После опер. ослож'              ], CReportBase.AlignLeft),
            ( ' 5%', [u'Исход',             u'Выписано' ], CReportBase.AlignLeft),
            ( ' 5%', [u'',                  u'Умерло'   ], CReportBase.AlignLeft),
            ( ' 5%', [u'',                  u'Переведен'], CReportBase.AlignLeft),
            ( ' 5%', [u'',                  u'На долеч' ], CReportBase.AlignLeft),
            ( ' 5%', [u'Умерло оперирован'              ], CReportBase.AlignLeft),
            ( ' 5%', [u'Послеоп. летал %'               ], CReportBase.AlignLeft),
            ( ' 5%', [u'Выздороление'                   ], CReportBase.AlignLeft),
            ( ' 5%', [u'Улучшение'                      ], CReportBase.AlignLeft),
            ( ' 5%', [u'Ухудшение'                      ], CReportBase.AlignLeft),
            ( ' 5%', [u'Без перемен'                    ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)
        countColumns = len(tableColumns)

        table.mergeCells(0, 8, 1, 4)
        for column in xrange(countColumns):
            if column < 8 or column > 11:
                table.mergeCells(0, column, 2, 1)

        currentOrgStructure = None
        countPerson = 0
        totalOrgStructure = [0]*(countColumns - 2)
        total = [0]*(countColumns - 2)
        while query.next():
            record = query.record()
            code = forceString(record.value('code'))
            person = forceString(record.value('person'))
            leaved = forceInt(record.value('leaved'))
            operation = forceInt(record.value('operation'))
            operationClient = forceInt(record.value('operationClient'))
            resultDischarged = forceInt(record.value('resultDischarged'))
            resultDead = forceInt(record.value('resultDead'))
            resultTransferred = forceInt(record.value('resultTransferred'))
            resultContinued = forceInt(record.value('resultContinued'))
            resultRecovery = forceInt(record.value('resultRecovery'))
            resultImprovement = forceInt(record.value('resultImprovement'))
            resultDeterioration = forceInt(record.value('resultDeterioration'))
            resultStatic = forceInt(record.value('resultStatic'))

            i = table.addRow()
            if currentOrgStructure != code:
                if currentOrgStructure is not None:
                    table.setText(i, 1, u'Итого', CReportBase.TableTotal)
                    for column, value in enumerate(totalOrgStructure):
                        if column in [3, 11]:
                            if column == 3:
                                table.setText(i, column + 2, forceDouble((totalOrgStructure[column - 1] * 100)/totalOrgStructure[column - 2]) if totalOrgStructure[column - 2] else 0, CReportBase.TableTotal)
                            else:
                                table.setText(i, column + 2, forceDouble((totalOrgStructure[column - 1] * 100)/totalOrgStructure[2]) if totalOrgStructure[2] else 0, CReportBase.TableTotal)
                            continue
                        total[column] += value
                        table.setText(i, column + 2, value, CReportBase.TableTotal)
                    totalOrgStructure = [0]*(countColumns - 2)
                    table.mergeCells(i - countPerson, 0, countPerson + 1, 1)
                    i = table.addRow()
                table.setText(i, 0, code)
                currentOrgStructure = code
                countPerson = 0

            table.setText(i,  1, person)
            table.setText(i,  2, leaved)
            table.setText(i,  3, operation)
            table.setText(i,  4, operationClient)
            table.setText(i,  5, forceDouble((operationClient * 100)/operation if operation else 0))
            table.setText(i,  8, resultDischarged)
            table.setText(i,  9, resultDead)
            table.setText(i, 10, resultTransferred)
            table.setText(i, 11, resultContinued)
            table.setText(i, 12, resultDead)
            table.setText(i, 13, forceDouble((resultDead * 100)/operationClient if operationClient else 0))
            table.setText(i, 14, resultRecovery)
            table.setText(i, 15, resultImprovement)
            table.setText(i, 16, resultDeterioration)
            table.setText(i, 17, resultStatic)

            totalOrgStructure[0] += leaved
            totalOrgStructure[1] += operation
            totalOrgStructure[2] += operationClient
            totalOrgStructure[6] += resultDischarged
            totalOrgStructure[7] += resultDead
            totalOrgStructure[8] += resultTransferred
            totalOrgStructure[9] += resultContinued
            totalOrgStructure[10] += resultDead
            totalOrgStructure[12] += resultRecovery
            totalOrgStructure[13] += resultImprovement
            totalOrgStructure[14] += resultDeterioration
            totalOrgStructure[15] += resultStatic
            countPerson += 1

        i = table.addRow()
        table.setText(i, 1, u'Итого', CReportBase.TableTotal)
        for column, value in enumerate(totalOrgStructure):
            if column in [3, 11]:
                if column == 3:
                    table.setText(i, column + 2, forceDouble((totalOrgStructure[column - 1] * 100)/totalOrgStructure[column - 2]) if totalOrgStructure[column - 2] else 0, CReportBase.TableTotal)
                else:
                    table.setText(i, column + 2, forceDouble((totalOrgStructure[column - 1] * 100)/totalOrgStructure[2]) if totalOrgStructure[2] else 0, CReportBase.TableTotal)
                continue
            total[column] += value
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        table.mergeCells(i - countPerson, 0, countPerson + 1, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(total):
            if column in [3, 11]:
                if column == 3:
                    table.setText(i, column + 2, forceDouble((total[column - 1] * 100)/total[column - 2]) if total[column - 2] else 0, CReportBase.TableTotal)
                else:
                    table.setText(i, column + 2, forceDouble((total[column - 1] * 100)/total[2]) if total[2] else 0, CReportBase.TableTotal)
                continue
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        return doc

class CSurgicalIndicators(QtGui.QDialog, Ui_ReportSurgicalIndicators):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstOrgStructure.setTable('OrgStructure')
        self.cmbFinance.setTable('rbFinance')
        self.cmbSpeciality.setTable('rbSpeciality', filter='rbSpeciality.id IN (SELECT DISTINCT p.speciality_id FROM Person p WHERE p.deleted = 0 GROUP BY p.speciality_id)')
        self.lstSpeciality.setTable('rbSpeciality', filter='rbSpeciality.id IN (SELECT DISTINCT p.speciality_id FROM Person p WHERE p.deleted = 0 GROUP BY p.speciality_id)')
        self.lstOperation.setTable('ActionType', filter=u'ActionType.serviceType = 4')
        self.cmbOperation.setTable('ActionType', filter=u'ActionType.serviceType = 4')


    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbTypeHosp.setCurrentIndex(params.get('typeHosp', 0))
        self.cmbOrder.setCurrentIndex(params.get('order', 0))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbOperation.setValue(params.get('operationId', None))
        self.chkSpeciality.setChecked(params.get('chkSpeciality', False))
        self.chkOrgStructure.setChecked(params.get('cmbOrgStructure', False))
        self.chkOperation.setChecked(params.get('cmbOperation', False))
        self.on_chkOrgStructure_clicked(self.chkOrgStructure.isChecked())
        self.on_chkOperation_clicked(self.chkOperation.isChecked())
        self.on_chkSpeciality_clicked(self.chkSpeciality.isChecked())
        self.cmbFinance.setValue(params.get('financeId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['typeHosp'] = self.cmbTypeHosp.currentIndex()
        result['order'] = self.cmbOrder.currentIndex()
        result['specialityId'] = self.cmbSpeciality.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['operationId'] = self.cmbOperation.value()
        result['lstSpeciality'] = self.lstSpeciality.nameValues()
        result['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        result['lstOperation'] = self.lstOperation.nameValues()
        result['chkSpeciality'] = self.chkSpeciality.isChecked()
        result['cmbOperation'] = self.chkOperation.isChecked()
        result['cmbOrgStructure'] = self.chkOrgStructure.isChecked()
        result['financeId'] = self.cmbFinance.value()
        return result

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkOperation_clicked(self, checked):
        self.lstOperation.setVisible(checked)
        self.cmbOperation.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkSpeciality_clicked(self, checked):
        self.lstSpeciality.setVisible(checked)
        self.cmbSpeciality.setVisible(not checked)

