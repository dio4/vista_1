# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceInt, forceString

from Orgs.Utils                         import getOrgStructureDescendants

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase

from Ui_ReportOperation import Ui_ReportOperation

def selectData(params, lstOrgStructure, lstOperation):
    db = QtGui.qApp.db

    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    # groupPerson = params.get('groupPerson')
    groupOrgStructure = params.get('groupOrgStructure')
    orgStructureId = params.get('orgStructureId')
    personId= params.get('personId')
    cmbOperation = params.get('cmbOperation')
    cmbOrgStructure = params.get('cmbOrgStructure')
    operationId = params.get('operationId')
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)

    tableAction = db.table('Action')
    tableOrgStructure = db.table('OrgStructure')
    tableOperation = db.table('ActionType')
    tablePerson = db.table('Person')

    cond = [tableAction['endDate'].dateGe(begDate),
            tableAction['endDate'].dateLe(endDate),
            'age(Client.birthDate, Action.begDate) >= %s' % ageFrom,
            'age(Client.birthDate, Action.begDate) <= %s' % ageTo]

    if groupOrgStructure:
        codeCol = u'''COALESCE(OrgStructure.code, 'Без подразделения') AS code'''
        orgStructurePart = u'''
                    LEFT JOIN (SELECT act_moving.deleted, act_moving.event_id, act_moving.begDate, act_moving.endDate, OrgStructure.code from Action act_moving
                    INNER JOIN ActionType at_moving ON at_moving.id = act_moving.actionType_id AND at_moving.flatCode = 'moving' AND at_moving.deleted = 0
                    INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = at_moving.id AND ActionPropertyType.name = 'Отделение пребывания' AND ActionPropertyType.deleted = 0
                    INNER JOIN ActionProperty ON ActionProperty.action_id = act_moving.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                    INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value) OrgStructure ON OrgStructure.event_id = Event.id AND OrgStructure.begDate <= Action.begDate AND (OrgStructure.endDate >= Action.endDate OR OrgStructure.endDate IS NULL) AND OrgStructure.deleted = 0
        '''
    else:
        codeCol = u'''IF(Person.id IS NOT NULL, CONCAT_WS(\' \', Person.lastName, Person.firstName, Person.patrName), 'Без исполнителя') AS code'''
        orgStructurePart = u'''
                    LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
        '''

    if lstOrgStructure and cmbOrgStructure:
        cond.append(tableOrgStructure['id'].inlist(lstOrgStructure))
    if lstOperation and cmbOperation:
        cond.append(tableOperation['id'].inlist(lstOperation))
    if orgStructureId and not cmbOrgStructure:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if operationId and not cmbOperation:
        cond.append(tableOperation['id'].eq(operationId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))

    stmt = u'''SELECT %s,
                      ActionType.name,
                      COUNT(DISTINCT IF(Event.order = 1, Event.id, NULL)) AS plan,
                      COUNT(DISTINCT IF(Event.order = 2, Action.id, NULL)) AS extra
               FROM ActionType
                    INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
                    INNER JOIN Person ON Person.id = Action.person_id
                    INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
                    INNER JOIN Client ON Client.id = Event.client_id
                    %s
               WHERE ActionType.serviceType = 4 AND %s AND ActionType.deleted = 0
               GROUP BY code, ActionType.id
               ORDER BY code, ActionType.name''' % (codeCol, orgStructurePart, db.joinAnd(cond))

    return db.query(stmt)

class CReportOperation(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Перечень операций, выполненных врачом-хирургом')

    def getSetupDialog(self, parent):
        result = COperation(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        lstOperationDict = params.get('lstOperation', None)
        lstOperation = lstOperationDict.keys()

        query = selectData(params, lstOrgStructure, lstOperation)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '10%', [u'ФИО врача' if params.get('groupPerson') else u'Подразделение'], CReportBase.AlignLeft),
            ( '20%', [u'Название операции'                                           ], CReportBase.AlignRight),
            ( ' 5%', [u'Количество', u'План.'                                        ], CReportBase.AlignLeft),
            ( ' 5%', [u'',           u'Экстр'                                        ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)
        countColumns = len(tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 2)

        currentCode = None
        countActionType = 0
        subTotal = [0]*(countColumns - 2)
        total = [0]*(countColumns - 2)
        while query.next():
            record = query.record()
            code  = forceString(record.value('code'))
            name  = forceString(record.value('name'))
            plan  = forceInt(record.value('plan'))
            extra = forceInt(record.value('extra'))

            i = table.addRow()
            if currentCode != code:
                if currentCode is not None:
                    table.setText(i, 1, u'Итого', CReportBase.TableTotal)
                    for column, value in enumerate(subTotal):
                        total[column] += value
                        table.setText(i, column + 2, value, CReportBase.TableTotal)
                    table.mergeCells(i - countActionType, 0, countActionType + 1, 1)
                    i = table.addRow()
                    subTotal = [0]*(countColumns - 2)
                table.setText(i, 0, code)
                currentCode = code
                countActionType = 0

            table.setText(i, 1, name)
            table.setText(i, 2, plan)
            table.setText(i, 3, extra)

            subTotal[0] += plan
            subTotal[1] += extra
            countActionType += 1

        i = table.addRow()
        table.setText(i, 1, u'Итого', CReportBase.TableTotal)
        for column, value in enumerate(subTotal):
            total[column] += value
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        table.mergeCells(i - countActionType, 0, countActionType + 1, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(total):
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        return doc

class COperation(QtGui.QDialog, Ui_ReportOperation):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstOrgStructure.setTable('OrgStructure')
        self.lstOperation.setTable('ActionType', filter=u'ActionType.serviceType = 4')
        self.cmbOperation.setTable('ActionType', filter=u'ActionType.serviceType = 4')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbOperation.setValue(params.get('operationId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkOrgStructure.setChecked(params.get('cmbOrgStructure', False))
        self.chkOperation.setChecked(params.get('cmbOperation', False))
        self.btnOrgStructure.setChecked(params.get('chkOrgStructure', False))
        self.on_chkOrgStructure_clicked(self.chkOrgStructure.isChecked())
        self.on_chkOperation_clicked(self.chkOperation.isChecked())
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['operationId'] = self.cmbOperation.value()
        result['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        result['lstOperation'] = self.lstOperation.nameValues()
        result['cmbOperation'] = self.chkOperation.isChecked()
        result['cmbOrgStructure'] = self.chkOrgStructure.isChecked()
        result['groupPerson'] = self.btnPerson.isChecked()
        result['groupOrgStructure'] = self.btnOrgStructure.isChecked()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkOperation_clicked(self, checked):
        self.lstOperation.setVisible(checked)
        self.cmbOperation.setVisible(not checked)





