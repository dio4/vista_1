# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################



from PyQt4 import QtCore, QtGui

from library.Utils                      import forceDouble, forceInt, forceString

from Orgs.Utils                         import getOrgStructureDescendants

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase

from Ui_ReportDiagnosisLeaved import Ui_ReportDiagnosisLeaved

column_keys = (
    'OrgStructure',
    'Diagnosis',
    'Weight',
    'CountAmb',

    'CountAdult',
    'DurationAdult',
    'CountAdultDead',
    'AdultOther',

    'CountChildren',
    'CountChildren1year',
    'DurationChildren',
    'CountChildrenDead',
    'CountChildren1yearDead',
    'ChildrenOther',
    'Children1yearOther'
)

def selectData(params, lstOrgStructure):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    order           = params.get('order')
    orgStructureId  = params.get('orgStructureId')
    typeHosp        = params.get('typeHosp')
    cmbOrgStructure = params.get('cmbOrgStructure')
    financeId       = params.get('financeId')
    MKBFilter = params.get('MKBFilter', 0)
    MKBFrom   = params.get('MKBFrom', '')
    MKBTo     = params.get('MKBTo', '')

    tableAction = db.table('Action')
    tableAct = db.table('Action').alias('act')

    cond =[tableAction['endDate'].dateGe(begDate),
           tableAction['endDate'].dateLe(endDate)]

    if order:
        tableEvent = db.table('Event')
        cond.append(tableEvent['order'].eq(order))
    if typeHosp == 1:
        cond.extend([u'OrgStructure.hasDayStationary = 0', 'OrgStructure.type != 4'])
    elif typeHosp == 2:
        cond.append(u'OrgStructure.hasDayStationary = 1')
    elif typeHosp == 3:
        cond.append('aps.value IS NOT NULL')
    if lstOrgStructure and cmbOrgStructure:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].inlist(lstOrgStructure))
    if orgStructureId and not cmbOrgStructure:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if financeId:
        cond.append(tableAction['finance_id'].eq(financeId))
    if MKBFilter:
        cond.append(tableAct['MKB'].between(MKBFrom, MKBTo))

    stmt = u'''SELECT OrgStructure.code, CONCAT_WS(' ', MKB_Tree.DiagName, MKB_Tree.DiagID) AS diag,
                      COUNT(Action.id) AS leaved,
                      COUNT(IF(age(Client.birthDate, Action.endDate) >= 18, Action.id, NULL)) AS countAdult,
                      sum(if(age(Client.birthDate, Action.endDate) >= 18, IF(OrgStructure.hasDayStationary = 1, datediff(Event.execDate, Event.setDate) + 1, datediff(Event.execDate, Event.setDate)), 0)) AS durationAdult,
                      COUNT(IF(age(Client.birthDate, Action.endDate) >= 18 AND apsResult.value = 'умер', Action.id, NULL)) AS countAdultDead,
                      COUNT(IF(age(Client.birthDate, Action.endDate) >= 18 AND apsResult.value = 'переведен в другой стационар', Action.id, NULL)) AS countAdultOther,
                      COUNT(IF(age(Client.birthDate, Action.endDate) < 18, Action.id, NULL)) AS countChildren,
                      sum(if(age(Client.birthDate, Action.endDate) < 18, IF(OrgStructure.hasDayStationary = 1, datediff(Event.execDate, Event.setDate) + 1, datediff(Event.execDate, Event.setDate)), 0)) AS durationChildren,
                      COUNT(IF(age(Client.birthDate, Action.endDate) < 1, Action.id, NULL)) AS countChildren1year,
                      COUNT(IF(age(Client.birthDate, Action.endDate) < 18 AND apsResult.value = 'умер', Action.id, NULL)) AS countChildrenDead,
                      COUNT(IF(age(Client.birthDate, Action.endDate) < 1 AND apsResult.value = 'умер', Action.id, NULL)) AS countChildren1yearDead,
                      COUNT(IF(age(Client.birthDate, Action.endDate) < 18 AND apsResult.value = 'переведен в другой стационар', Action.id, NULL)) AS countChildrenOther,
                      COUNT(IF(age(Client.birthDate, Action.endDate) < 1 AND apsResult.value = 'переведен в другой стационар', Action.id, NULL)) AS countChildren1yearOther,
                      COUNT(IF(aps.value IS NOT NULL, Action.id, NULL)) AS coutAmb
                FROM ActionType
                      INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
                      INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
                      INNER JOIN Client ON Client.id = Event.client_id
                      INNER JOIN Action act ON act.event_id = Action.event_id AND act.id = (SELECT MAX(a.id)
                                                                                              FROM ActionType at
                                                                                              INNER JOIN Action a ON a.actionType_id = at.id AND a.deleted = 0
                                                                                              WHERE a.event_id = Event.id AND at.flatCode = 'moving' AND at.deleted = 0)
                      INNER JOIN ActionProperty ON ActionProperty.action_id = act.id AND ActionProperty.type_id = (SELECT apt.id
                                                                                                                    FROM ActionPropertyType apt
                                                                                                                    WHERE apt.actionType_id = act.actionType_id AND apt.name = 'Отделение пребывания' AND apt.deleted = 0) AND ActionProperty.deleted = 0
                      INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                      INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                      LEFT JOIN MKB_Tree ON MKB_Tree.DiagID = act.MKB
                      LEFT JOIN ActionProperty apResult ON apResult.action_id = Action.id AND apResult.type_id = (SELECT apt.id
                                                                                                                  FROM ActionPropertyType apt
                                                                                                                  WHERE apt.actionType_id = Action.actionType_id AND apt.name = 'Исход госпитализации' AND apt.deleted = 0) AND apResult.deleted = 0
                      LEFT JOIN ActionProperty_String apsResult ON apsResult.id = apResult.id
                      LEFT JOIN Action act_received ON act_received.event_id = Event.id AND act_received.actionType_id = (SELECT at.id
                                                                                                                                          FROM ActionType at
                                                                                                                                          WHERE at.flatCode = 'received' AND at.deleted = 0) AND act_received.deleted = 0
                      LEFT JOIN ActionProperty ap ON ap.action_id = act_received.id AND ap.type_id = (SELECT apt.id
                                                                                                                        FROM ActionPropertyType apt
                                                                                                                        INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND at.deleted = 0
                                                                                                                        WHERE apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0)
                      LEFT JOIN ActionProperty_String aps ON aps.id = ap.id
                WHERE ActionType.flatCode = 'leaved' AND %s AND ActionType.deleted = 0
                GROUP BY OrgStructure.id, act.MKB ''' % db.joinAnd(cond)
    return db.query(stmt)

class CReportDiagnosisLeaved(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Состав больных в стационаре, сроки и исходы лечения среди выбывших (по диагнозу оплаты)')

    def getSetupDialog(self, parent):
        result = CDiagnosisLeaved(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        query = selectData(params, lstOrgStructure)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Отделение'                 ], CReportBase.AlignLeft),
            ('20%',  [u'Диагноз'                   ], CReportBase.AlignLeft),
            (' 3%',  [u'Удельный вес заболев.'     ], CReportBase.AlignRight),
            (' 3%',  [u'Выписано б-х'              ], CReportBase.AlignRight),
            (' 3%',  [u'Провед выпис. к/д'         ], CReportBase.AlignRight),
            (' 3%',  [u'Умерло'                    ], CReportBase.AlignRight),
            (' 3%',  [u'Переведено'                ], CReportBase.AlignRight),
            (' 3%',  [u'Выписано б-х'              ], CReportBase.AlignRight),
            (' 3%',  [u'В т.ч до 1 года'           ], CReportBase.AlignRight),
            (' 3%',  [u'Провед выпис. к/д'         ], CReportBase.AlignRight),
            (' 3%',  [u'Умерло'                    ], CReportBase.AlignRight),
            (' 3%',  [u'В т.ч до 1 года'           ], CReportBase.AlignRight),
            (' 3%',  [u'Переведено'                ], CReportBase.AlignRight),
            (' 3%',  [u'В т.ч до 1 года'           ], CReportBase.AlignRight),
            (' 3%',  [u'Кроме того, амбулаторных'  ], CReportBase.AlignRight)]
        # Фильтрация столбцов
        isGeneral = params.get('isGeneral')
        general_cols_mask = params.get('general')
        general_cols_filtered = []
        if isGeneral:
            general_cols = zip(column_keys[:4], (tableColumns[:3] + [tableColumns[-1]]))
            general_cols_filtered = filter(lambda item: general_cols_mask[item[0]], general_cols)
        else:
            general_cols_mask = dict(zip(general_cols_mask.keys(), [False]*len(general_cols_mask)))
        isGeneral = bool(len(general_cols_filtered))
        isAdult = params.get('isAdult')
        adult_cols_mask = params.get('adult')
        adult_cols_filtered = []
        if isAdult:
            adult_cols = zip(column_keys[4:8], (tableColumns[3:7]))
            adult_cols_filtered = filter(lambda item: adult_cols_mask[item[0]], adult_cols)
        else:
            adult_cols_mask = dict(zip(adult_cols_mask.keys(), [False]*len(adult_cols_mask)))
        isAdult = bool(len(adult_cols_filtered))
        isChildren = params.get('isChildren')
        children_cols_filtered = []
        children_cols_mask = params.get('children')
        if isChildren:
            children_cols = zip(column_keys[8:], (tableColumns[7:-1]))
            children_cols_filtered = filter(lambda item: children_cols_mask[item[0]], children_cols)
        else:
            children_cols_mask = dict(zip(children_cols_mask.keys(), [False]*len(children_cols_mask)))
        isChildren = bool(len(children_cols_filtered))

        all_mask = {}
        all_mask.update(general_cols_mask)
        all_mask.update(adult_cols_mask)
        all_mask.update(children_cols_mask)

        # Добавление столбцов
        totalCols = []
        ambCol = None
        if isGeneral:
            ambCol = general_cols_filtered[-1][1] if general_cols_filtered[-1][0] == 'CountAmb' else None
            if ambCol:
                general_cols_filtered = general_cols_filtered[:-1]
            for key, col in general_cols_filtered:
                totalCols.append(col)
        if isAdult:
            first_col = adult_cols_filtered[0][1]
            first_col = (first_col[0], [u'А.Взрослые'] + first_col[1], first_col[2])
            totalCols.append(first_col)
            if len(adult_cols_filtered) >= 2:
                for key, col in adult_cols_filtered[1:]:
                    col = (col[0], [u''] + col[1], col[2])
                    totalCols.append(col)
        if isChildren:
            first_col = children_cols_filtered[0][1]
            first_col = (first_col[0], [u'Б.Дети и подростки до 17 лет включительно'] + first_col[1], first_col[2])
            totalCols.append(first_col)
            if len(children_cols_filtered) >= 2:
                for key, col in children_cols_filtered[1:]:
                    col = (col[0], [u''] + col[1], col[2])
                    totalCols.append(col)
        if ambCol:
            totalCols.append(ambCol)
        table = createTable(cursor, totalCols)
        countColumns = len(totalCols)
        countColumnsTotal = 15

        # Объединение столбцов
        gen_count = 0
        if general_cols_mask['OrgStructure']:
            table.mergeCells(0,  gen_count, 2, 1)
            gen_count += 1
        if general_cols_mask['Diagnosis']:
            table.mergeCells(0,  gen_count, 2, 1)
            gen_count += 1
        if general_cols_mask['Weight']:
            table.mergeCells(0,  gen_count, 2, 1)
            gen_count += 1
        adult_count = len(adult_cols_filtered)
        if isAdult:
            table.mergeCells(0,  gen_count, 1, adult_count)
        children_count = len(children_cols_filtered)
        if isChildren:
            table.mergeCells(0,  gen_count + adult_count, 1, children_count)
        if ambCol:
            table.mergeCells(0, countColumns - 1, 2, 1)

        currentOrgStructure = None
        countDiagnosis = 0
        totalOrgStructure = [0]*(countColumnsTotal - 3)
        totalOrgStructureFiltered = [0] * (countColumns - 3)
        total = [0]*(countColumnsTotal - 3)
        totalFiltered = [0]*(countColumns - 3)
        leaved = []

        while query.next():
            record = query.record()
            fields = zip(column_keys, (
                forceString(record.value('code')),
                forceString(record.value('diag')),
                '',
                forceInt(record.value('coutAmb')),
                forceInt(record.value('countAdult')),
                forceInt(record.value('durationAdult')),
                forceInt(record.value('countAdultDead')),
                forceInt(record.value('countAdultOther')),
                forceInt(record.value('countChildren')),
                forceInt(record.value('countChildren1year')),
                forceInt(record.value('durationChildren')),
                forceInt(record.value('countChildrenDead')),
                forceInt(record.value('countChildren1yearDead')),
                forceInt(record.value('countChildrenOther')),
                forceInt(record.value('countChildren1yearOther'))
            ))
            fields = fields[:3] + fields[4:] + [fields[3]]
            fields_filtered = filter(lambda item: all_mask[item[0]], fields)

            orgStructure = fields[0][1]
            leaved.append(forceInt(record.value('leaved')))

            i = table.addRow()
            if currentOrgStructure != orgStructure:
                if currentOrgStructure is not None:
                    leaved.insert(len(leaved) - 1, u'-')
                    table.setText(i, 1, u'Итого', CReportBase.TableTotal)
                    for column, value in enumerate(totalOrgStructure):
                        total[column] += value
                    for column, value in enumerate(totalOrgStructureFiltered):
                        totalFiltered[column] += value
                        table.setText(i, column + 3, value if value else '', CReportBase.TableTotal)
                    table.mergeCells(i - countDiagnosis, 0, countDiagnosis + 1, 1)
                    i = table.addRow()
                totalOrgStructure = [0] * (countColumnsTotal - 3)
                totalOrgStructureFiltered = [0] * (countColumns - 3)
                table.setText(i, 0, orgStructure)
                currentOrgStructure = orgStructure
                countDiagnosis = 0

            for col, (key, value) in enumerate(fields[3:]):
                totalOrgStructure[col] += value

            for col, (key, value) in enumerate(fields_filtered[1:]):
                table.setText(i,  col + 1, value if value else '')
                if col not in [0, 1]:
                    totalOrgStructureFiltered[col - 2] += value

            countDiagnosis += 1

        i = table.addRow()
        table.setText(i, 1, u'Итого', CReportBase.TableTotal)
        for column, value in enumerate(totalOrgStructureFiltered):
            totalFiltered[column] += value
            table.setText(i, column + 3, value if value else '', CReportBase.TableTotal)
        for column, value in enumerate(totalOrgStructure):
            total[column] += value
        table.mergeCells(i - countDiagnosis, 0, countDiagnosis + 1, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(totalFiltered):
            table.setText(i, column + 3, value if value else '', CReportBase.TableTotal)
        if all_mask['Weight']:
            for row, value in enumerate(leaved):
                if value != u'-' and value:
                    table.setText(row + 2, 2, round(forceDouble(value/forceDouble(total[0]+total[4]))*100, 2))
        return doc


class CDiagnosisLeaved(QtGui.QDialog, Ui_ReportDiagnosisLeaved):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstOrgStructure.setTable('OrgStructure')
        self.cmbFinance.setTable('rbFinance')
        # The first two columns set always visible (for a while)
        self.gbGeneral.setCheckable(False)
        self.chkOrgStructure.setEnabled(False)
        self.chkDiagnosis.setEnabled(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbTypeHosp.setCurrentIndex(params.get('typeHosp', 0))
        self.cmbOrder.setCurrentIndex(params.get('order', 0))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('financeId', None))
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        self.chkOrgStructureMulti.setChecked(params.get('cmbOrgStructure', False))
        self.on_chkOrgStructureMulti_clicked(self.chkOrgStructureMulti.isChecked())
        all_chks = {}
        all_chks.update(params.get('general', {}))
        all_chks.update(params.get('adult', {}))
        all_chks.update(params.get('children', {}))
        for key in all_chks:
            self.callObjectAtributeMethod('chk%s' % key, 'setChecked', all_chks[key])
            if key.find('1year') != -1:
                self.callObjectAtributeMethod('chk%s' % key, 'setEnabled', all_chks[key.replace('1year', '')])
        for key in ['General', 'Adult', 'Child']:
            self.callObjectAtributeMethod('gb%s' % key, 'setChecked', params.get('is%s' % key, True))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['typeHosp'] = self.cmbTypeHosp.currentIndex()
        result['order'] = self.cmbOrder.currentIndex()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        result['cmbOrgStructure'] = self.chkOrgStructureMulti.isChecked()
        result['financeId'] = self.cmbFinance.value()
        result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
        result['MKBFrom'] = forceString(self.edtMKBFrom.text())
        result['MKBTo'] = forceString(self.edtMKBTo.text())
        # General (is active always for now)
        result['isGeneral'] = True
        result['general'] = dict.fromkeys(column_keys[:4], False)
        for key in result['general']:
            result['general'][key] = self.callObjectAtributeMethod('chk%s' % key, 'isChecked')
        # Adult
        result['isAdult'] = self.gbAdult.isChecked()
        result['adult'] = dict.fromkeys(column_keys[4:8], False)
        for key in result['adult']:
            result['adult'][key] = self.callObjectAtributeMethod('chk%s' % key, 'isChecked')
        # Children
        result['isChildren'] = self.gbChild.isChecked()
        result['children'] = dict.fromkeys(column_keys[8:], False)
        for key in result['children']:
            result['children'][key] = self.callObjectAtributeMethod('chk%s' % key, 'isChecked')
        return result

    def callObjectAtributeMethod(self, objectName, nameMethod, *args):
        return self.__getattribute__(objectName).__getattribute__(nameMethod)(*args)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructureMulti_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)

    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)

    @QtCore.pyqtSlot(bool)
    def on_chkCountChildren_clicked(self, checked):
        self.chkCountChildren1year.setEnabled(checked)
        self.chkCountChildren1year.setChecked(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkCountChildrenDead_clicked(self, checked):
        self.chkCountChildren1yearDead.setEnabled(checked)
        self.chkCountChildren1yearDead.setChecked(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkChildrenOther_clicked(self, checked):
        self.chkChildren1yearOther.setEnabled(checked)
        self.chkChildren1yearOther.setChecked(checked)