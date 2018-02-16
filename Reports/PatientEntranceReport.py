# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceString, forceInt
from Orgs.Utils         import getOrganisationInfo
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_PatientEntranceSetup import Ui_PatientEntranceSetupDialog
from library.StrComboBox import CStrComboBox
from library.vm_collections import OrderedDict


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    begTime = params.get('begTime', QtCore.QTime())
    endTime = params.get('endTime', QtCore.QTime())

    begDateTime = QtCore.QDateTime(begDate, begTime)
    endDateTime = QtCore.QDateTime(endDate, endTime)

    tableAction = db.table('Action').alias('a')

    cond = [tableAction['begDate'].datetimeGe(begDateTime),
            tableAction['begDate'].datetimeLe(endDateTime)]

    # получаем id отделения из выпадающего списка, и если у него есть дочерние подразделения то добавляем их в условие поиска
    orgStruct = forceString(params.get('orgStruct'))
    if orgStruct:
        children_list = db.getColumnValues('OrgStructure_Ancestors','id',where="fullPath RLIKE '[[:<:]]%s[[:>:]]'" % orgStruct, handler=forceInt)
        children_list.append(int(orgStruct))
        tableOrgStructure = db.table('OrgStructure').alias('os')
        cond.append(tableOrgStructure['id'].inlist(children_list))

    stmt = u"""SELECT
    os.name as org_struct,
    aps.value as patient_state
    FROM
    Action a
    INNER JOIN
    ActionType at ON at.id = a.actionType_id AND at.flatCode = 'received'
    LEFT JOIN
    ActionPropertyType apt1 ON apt1.actionType_id = at.id AND apt1.name = 'Направлен в отделение'
    LEFT JOIN
    ActionPropertyType apt2 ON apt2.actionType_id = at.id AND apt2.name = 'Cостояние пациента'
    LEFT JOIN
    ActionProperty ap1 ON ap1.type_id = apt1.id AND ap1.action_id = a.id
    LEFT JOIN
    ActionProperty ap2 ON ap2.type_id = apt2.id AND ap2.action_id = a.id
    LEFT JOIN
    ActionProperty_String aps ON aps.id = ap2.id
    LEFT JOIN
    ActionProperty_OrgStructure apos ON apos.id = ap1.id
    LEFT JOIN
    OrgStructure os ON os.id = apos.value
    WHERE %s
    AND a.deleted = 0
    ORDER BY org_struct
    """ % (db.joinAnd(cond))
    return db.query(stmt)


class CPatientEntranceReport(CReport):
    def __init__(self, parent):
        super(CPatientEntranceReport, self).__init__(parent)
        self.setTitle(u'Поступление больных по тяжести состояния')

    def getSetupDialog(self, parent):
        result = CPatientEntranceReportSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)

        org_id = QtGui.qApp.currentOrgId()
        org_info = getOrganisationInfo(org_id)

        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(org_info.get('fullName'))
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(self.title())

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [('20%', [u'Отделение'], CReportBase.AlignCenter)]

        valueDomain = QtGui.qApp.db.translate('ActionPropertyType', 'name', u'Cостояние пациента', 'valueDomain')
        state_list = CStrComboBox.parse(forceString(valueDomain))[0]
        state_list.insert(0, u'')
        for header in state_list:
            tableColumns.append(('12%', [header], CReportBase.AlignCenter))

        tableColumns.append(('8%',   [u'Всего'], CReportBase.AlignCenter))
        table = createTable(cursor, tableColumns)
        struct = OrderedDict()
        while query.next():
            record = query.record()
            org_struct = forceString(record.value('org_struct'))
            org_struct = org_struct if org_struct else u'без уточнения'
            patient_state = forceString(record.value('patient_state'))
            d = struct.setdefault(org_struct, OrderedDict.fromkeys(state_list, 0))
            d[patient_state] += 1

        total_col = OrderedDict.fromkeys(state_list, 0)
        total_col['total'] = 0
        for org_struct, d in struct.items():
            i = table.addRow()
            table.setText(i, 0, org_struct)
            total_row = 0
            for col, (state, num) in enumerate(d.items()):
                table.setText(i, col+1, num)
                total_row += num
                total_col[state] += num
            table.setText(i, len(d)+1, total_row)
            total_col['total'] += total_row
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        for col, N in enumerate(total_col.values()):
            table.setText(i, col+1, N, CReportBase.TableTotal)

        return doc


class CPatientEntranceReportSetup(QtGui.QDialog, Ui_PatientEntranceSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def params(self):
        result = {'begDate' : self.edtBegDate.date(),
                  'endDate' : self.edtEndDate.date(),
                  'begTime' : self.edtBegTime.time(),
                  'endTime' : self.edtEndTime.time(),
                  'orgStruct': self.cmbOrgStructure.value()}
        return result

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime(8, 00)))
        self.edtEndTime.setTime(params.get('endTime', QtCore.QTime(7, 59)))
        self.cmbOrgStructure.setValue(params.get('orgStruct'))
