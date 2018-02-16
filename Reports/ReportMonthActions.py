# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Events.Action       import CActionType

from library.Utils      import forceDate, forceInt, forceRef, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_SetupReportMonthActions import Ui_SetupReportMonthActionsDialog


def selectData(params):
    db = QtGui.qApp.db

    date = params.get('date', QtCore.QDate.currentDate())
    financeId = params.get('financeId', None)
    class_ = params.get('class', None)
    actionTypeGroupId = params.get('actionTypeGroupId', None)
    if actionTypeGroupId:
        actionTypeGroupIdList = db.getDescendants('ActionType', 'group_id', actionTypeGroupId)
    else:
        actionTypeGroupIdList = None
    status = params.get('status', None)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    assistantId = params.get('assistantId', None)
    tissueTypeId = params.get('tissueTypeId', None)

    tableAction        = db.table('Action')
    tableActionType    = db.table('ActionType')
    tablePerson        = db.table('Person')
    tableTissueJournal = db.table('TakenTissueJournal')

    begDate = QtCore.QDate()
    begDate.setDate(date.year(), date.month(), 1)
    endDate = QtCore.QDate()
    endDate.setDate(date.year(), date.month(), date.daysInMonth())
    cond = [tableAction['endDate'].dateLe(endDate),
            tableAction['endDate'].dateGe(begDate),
            tableAction['deleted'].eq(0)]
    if financeId:
        cond.append(tableAction['finance_id'].eq(financeId))
    if not class_ is None:
        cond.append(tableActionType['class'].eq(class_))
    if actionTypeGroupIdList:
        cond.append(tableActionType['group_id'].inlist(actionTypeGroupIdList))
    if not status is None:
        cond.append(tableAction['status'].eq(status))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].eq(orgStructureId))
    if personId:
        cond.append(tableAction['person_id'].eq(personId))
    if assistantId:
        cond.append(u"EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND rbAAT.code like 'assistant'"
                                u"              AND A_A.person_id = %s)"  % (tableAction['id'].name(),
                                                                             assistantId))
    if tissueTypeId:
        if tissueTypeId == -1:
            cond.append(tableTissueJournal['tissueType_id'].isNotNull())
        else:
            cond.append(tableTissueJournal['tissueType_id'].eq(tissueTypeId))

    stmt = '''
SELECT
Action.`amount`, Action.`endDate`,
ActionType.`id` as actionTypeId, ActionType.`code`, ActionType.`name`,
ParentActionType.`id` AS parentActionTypeId,
ParentActionType.`code` AS parentActionTypeCode,
ParentActionType.`name` AS parentActionTypeName
FROM Action
INNER JOIN ActionType ON ActionType.`id` = Action.`actionType_id`
LEFT JOIN Person ON Person.`id` = Action.`setPerson_id`
LEFT JOIN ActionType AS ParentActionType ON ParentActionType.`id`=ActionType.`group_id`
LEFT JOIN TakenTissueJournal ON TakenTissueJournal.`id` = Action.`takenTissueJournal_id`
WHERE
Action.`deleted`=0 AND %s
ORDER BY parentActionTypeName, ActionType.`name`
''' % db.joinAnd(cond)
    return db.query(stmt)

class CReportMonthActions(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет об обслуживании за месяц')
        self.resetHelpers()



    def getSetupDialog(self, parent):
        result = CSetupReportMonthActions(parent)
        result.setTitle(self.title())
        return result

    def resetHelpers(self):
        self.parentActionTypesIdList = []
        self.mapActionTypeIdToName = {}
        self.mapParentToChildrens = {}
        self.mapActionTypesToValues = {}
        self.daysInMonth = 0

    def build(self, params):
        self.resetHelpers()
        date = params.get('date', QtCore.QDate.currentDate())
        self.daysInMonth = date.daysInMonth()
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.makeStructAction(query)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [('2%', [u'№'], CReportBase.AlignRight),
                        ('20%', [u'Наименование\nгруппы/действия'], CReportBase.AlignLeft)]
        daysColumns = [('2%', [unicode(colName+1)], CReportBase.AlignLeft) for colName in range(self.daysInMonth)]
        tableColumns.extend(daysColumns)
        tableColumns.extend([('3%', [u'Итого'], CReportBase.AlignRight)])

        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        iActionTypes = 1
        resultValues = [0]*(self.daysInMonth+1) # +1 - это колонка `итого`

        spaceShift = ' '*6
        for parentActionTypeId in self.parentActionTypesIdList:
            intermediateValues = [0]*(self.daysInMonth+1) # +1 - это колонка `итого`
            i = table.addRow()
            ationTypeBlockName = self.mapActionTypeIdToName.get(parentActionTypeId, u'')
            table.setText(i, 1, spaceShift+ationTypeBlockName, charFormat=boldChars)
            table.mergeCells(i, 0, 1, self.daysInMonth+3)

            for actionTypeId in self.mapParentToChildrens[parentActionTypeId]:
                i = table.addRow()
                table.setText(i, 0, iActionTypes)
                table.setText(i, 1, self.mapActionTypeIdToName.get(actionTypeId, u''))

                rowValue = 0
                for iDay, val in enumerate(self.mapActionTypesToValues[actionTypeId]):
                    val = val if val else u''
                    table.setText(i, iDay+2, val)
                    if bool(val):
                        intermediateValues[iDay] += val
                        resultValues[iDay] += val
                        rowValue += val
                intermediateValues[-1] += rowValue
                table.setText(i, self.daysInMonth+2, rowValue)
                iActionTypes += 1
            resultValues [-1] += intermediateValues[-1]

            i = table.addRow()
            table.mergeCells(i, 0, 1, 2)
            table.setText(i, 1, u'Итого', charFormat=boldChars)
            for iDay, val in enumerate(intermediateValues):
                val = val if val else u''
                table.setText(i, iDay+2, val, charFormat=boldChars)

            cursor.setCharFormat(CReportBase.TableBody)

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 1, u'Всего', charFormat=boldChars)
        for iDay, val in enumerate(resultValues):
            val = val if val else u''
            table.setText(i, iDay+2, val, charFormat=boldChars)

        return doc


    def makeStructAction(self, query):
        while query.next():
            record = query.record()

            amount               = forceInt(record.value('amount'))
            date                 = forceDate(record.value('endDate'))

            parentActionTypeId   = forceRef(record.value('parentActionTypeId'))
            parentActionTypeCode = forceString(record.value('parentActionTypeCode'))
            parentActionTypeName = forceString(record.value('parentActionTypeName'))

            actionTypeId         = forceRef(record.value('actionTypeId'))
            actionTypeCode       = forceString(record.value('code'))
            actionTypeName       = forceString(record.value('name'))

            if not parentActionTypeId in self.parentActionTypesIdList:
                self.parentActionTypesIdList.append(parentActionTypeId)
                childrensList = self.mapParentToChildrens.get(parentActionTypeId, None)
                if childrensList:
                    childrensList.append(actionTypeId)
                else:
                    self.mapParentToChildrens[parentActionTypeId] = [actionTypeId]
                self.mapActionTypesToValues[actionTypeId] = [0]*self.daysInMonth
            else:
                childrensList = self.mapParentToChildrens[parentActionTypeId]
                if not actionTypeId in childrensList:
                    childrensList.append(actionTypeId)
                    self.mapActionTypesToValues[actionTypeId] = [0]*self.daysInMonth

            values = self.mapActionTypesToValues[actionTypeId]
#            amount = amount if amount else 1
            values[date.day()-1] += amount

            if not parentActionTypeId in self.mapActionTypeIdToName.keys():
                self.mapActionTypeIdToName[parentActionTypeId] = ' | '.join([parentActionTypeCode, parentActionTypeName])
            if not actionTypeId in self.mapActionTypeIdToName.keys():
                self.mapActionTypeIdToName[actionTypeId] = ' | '.join([actionTypeCode, actionTypeName])

    def getDescription(self, params):
        date = params.get('date', QtCore.QDate.currentDate())
        financeId = params.get('financeId', None)
        class_ = params.get('class', None)
        actionTypeGroupId = params.get('actionTypeGroupId', None)
        status = params.get('status', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        assistantId = params.get('assistantId', None)
        tissueTypeId = params.get('tissueTypeId', None)

        rows = [u'Год: %d'%date.year(),
                u'Месяц: %s'%[u'январь',
                              u'февраль',
                              u'март',
                              u'апрель',
                              u'май',
                              u'июнь',
                              u'июль',
                              u'август',
                              u'сентябрь',
                              u'октябрь',
                              u'ноябрь',
                              u'декабрь'][date.month()-1]]
        db = QtGui.qApp.db
        if financeId:
            rows.append(u'Тип финансирования: %s'%forceString(db.translate('rbFinance', 'id', financeId, 'name')))
        if not class_ is None:
            rows.append(u'Класс типов действия: %s'%[u'статус', u'диагностика', u'лечение', u'прочие мероприятия'][class_])
        if actionTypeGroupId:
            rows.append(u'Группа типов действий: %s'%forceString(db.translate('ActionType', 'id', actionTypeGroupId, 'CONCAT(code, \' | \', name)')))
        if not status is None:
            rows.append(u'Статус: %s' % CActionType.retranslateClass(False).statusNames[status])
        if orgStructureId:
            rows.append(u'Подразделение: %s'%forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name')))
        if personId:
            rows.append(u'Назначивший: %s'%forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')))
        if assistantId:
            rows.append(u'Ассистент: %s'%forceString(db.translate('vrbPersonWithSpeciality', 'id', assistantId, 'name')))
        if tissueTypeId:
            rows.append(u'Тип биоматериала: %s'%forceString(db.translate('rbTissueType', 'id', tissueTypeId, 'CONCAT(code, \' | \', name)')))
        return rows

class CSetupReportMonthActions(QtGui.QDialog, Ui_SetupReportMonthActionsDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbStatus.clear()
        self.cmbStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbTissueType.setTable('rbTissueType', addNone=True, specialValues=[(-1, u'-', u'Любой')])

        self.edtDate.setDisplayFormat('MM.yyyy')
        self.cmbActionTypeGroup.setClass(None)
        self.cmbActionTypeGroup.model().setLeavesVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtDate.setDate(params.get('date', QtCore.QDate.currentDate()))

        chkFinance = params.get('chkFinance', False)
        self.chkFinance.setChecked(chkFinance)
        self.chkFinance.emit(QtCore.SIGNAL('clicked(bool)'), chkFinance)
        self.cmbFinance.setValue(params.get('financeId', None))

        chkClass = params.get('chkClass', False)
        self.chkClass.setChecked(chkClass)
        self.chkClass.emit(QtCore.SIGNAL('clicked(bool)'), chkClass)
        self.cmbClass.setCurrentIndex(params.get('class', 0))

        chkActionTypeGroup = params.get('chkActionTypeGroup', False)
        self.chkActionTypeGroup.setChecked(chkActionTypeGroup)
        self.chkActionTypeGroup.emit(QtCore.SIGNAL('clicked(bool)'), chkActionTypeGroup)
        self.cmbActionTypeGroup.setValue(params.get('actionTypeGroupId', None))

        chkStatus = params.get('chkStatus', False)
        self.chkStatus.setChecked(chkStatus)
        self.chkStatus.emit(QtCore.SIGNAL('clicked(bool)'), chkStatus)
        self.cmbStatus.setCurrentIndex(params.get('status', 0))

        chkOrgStructure = params.get('chkOrgStructure', False)
        self.chkOrgStructure.setChecked(chkOrgStructure)
        self.chkOrgStructure.emit(QtCore.SIGNAL('clicked(bool)'), chkOrgStructure)
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

        chkPerson = params.get('chkPerson', False)
        self.chkPerson.setChecked(chkPerson)
        self.chkPerson.emit(QtCore.SIGNAL('clicked(bool)'), chkPerson)
        self.cmbPerson.setValue(params.get('personId', None))

        chkAssistant = params.get('chkAssistant', False)
        self.chkAssistant.setChecked(chkAssistant)
        self.chkAssistant.emit(QtCore.SIGNAL('clicked(bool)'), chkAssistant)
        self.cmbAssistant.setValue(params.get('assistantId', None))

        chkTissueType = params.get('chkTissueType', False)
        self.chkTissueType.setChecked(chkTissueType)
        self.chkTissueType.emit(QtCore.SIGNAL('clicked(bool)'), chkTissueType)
        self.cmbTissueType.setValue(params.get('tissueTypeId', None))


    def params(self):
        params = {}
        params['date'] = self.edtDate.date()

        params['chkFinance']    = self.chkFinance.isChecked()
        if params['chkFinance']:
            params['financeId'] = self.cmbFinance.value()

        params['chkClass']  = self.chkClass.isChecked()
        if params['chkClass']:
            params['class'] = self.cmbClass.currentIndex()

        params['chkActionTypeGroup']    = self.chkActionTypeGroup.isChecked()
        if params['chkActionTypeGroup']:
            params['actionTypeGroupId'] = self.cmbActionTypeGroup.value()

        params['chkStatus']  = self.chkStatus.isChecked()
        if params['chkStatus']:
            params['status'] = self.cmbStatus.currentIndex()

        params['chkOrgStructure']    = self.chkOrgStructure.isChecked()
        if params['chkOrgStructure']:
            params['orgStructureId'] = self.cmbOrgStructure.value()

        params['chkPerson']    = self.chkPerson.isChecked()
        if params['chkPerson']:
            params['personId'] = self.cmbPerson.value()

        params['chkAssistant']    = self.chkAssistant.isChecked()
        if params['chkAssistant']:
            params['assistantId'] = self.cmbAssistant.value()

        params['chkTissueType']    = self.chkTissueType.isChecked()
        if params['chkTissueType']:
            params['tissueTypeId'] = self.cmbTissueType.value()

        return params

    @QtCore.pyqtSlot(bool)
    def on_chkClass_clicked(self, bValue):
        if bValue:
            class_ = self.cmbClass.currentIndex()
        else:
            class_ = None
        self.cmbActionTypeGroup.setClass(class_)

    @QtCore.pyqtSlot(int)
    def on_cmbClass_currentIndexChanged(self, index):
        self.cmbActionTypeGroup.setClass(index)
