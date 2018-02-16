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

from Ui_ReportAgeSexCompositionLeavedClients import Ui_ReportAgeSexCompositionLeavedClients

def selectData(params):
    db = QtGui.qApp.db

    begDate           = params.get('begDate').toString(QtCore.Qt.ISODate)
    endDate           = params.get('endDate').toString(QtCore.Qt.ISODate)
    orgStructureId    = params.get('orgStructureId')
    profileBed        = params.get('profileBed')
    orderEvent        = params.get('order', None)
    typeHosp          = params.get('typeHosp')
    ungroupProfileBed = params.get('ungroupProfileBed')

    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableOrgStructure = db.table('OrgStructure')
    tableHospitalBedProfile = db.table('rbHospitalBedProfile')

    cond = [tableAction['endDate'].dateGe(begDate),
            tableAction['endDate'].dateLe(endDate)]
    group = ['OrgStructure.id']
    order = ['OrgStructure.code']

    if not ungroupProfileBed:
        group.append('rbHospitalBedProfile.id')
        order.append('rbHospitalBedProfile.name')

    if orderEvent:
        cond.append(tableEvent['order'].eq(orderEvent))
    if typeHosp == 1:
        cond.extend([u'OrgStructure.hasDayStationary = 0', 'OrgStructure.type != 4'])
    elif typeHosp == 2:
        cond.append(u'OrgStructure.hasDayStationary = 1')
    elif typeHosp == 3:
        cond.append('aps.value IS NOT NULL')
    if profileBed:
        cond.append(tableHospitalBedProfile['id'].eq(profileBed))
    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    cond.append(tableAction['deleted'].eq(0))

    stmt = u'''SELECT  OrgStructure.code
                      , rbHospitalBedProfile.name
                      , COUNT(Action.id) AS countEvent
                      , COUNT(IF(Client.sex = 1, Action.id, NULL)) AS countMen
                      , COUNT(IF(Client.sex = 1 AND age(Client.birthDate, Action.endDate) < 60, Action.id, NULL)) AS countMen60
                      , COUNT(IF(Client.sex = 1 AND age(Client.birthDate, Action.endDate) > 60, Action.id, NULL)) AS countMenAfter60
                      , COUNT(IF(Client.sex = 2, Action.id, NULL)) AS countWomen
                      , COUNT(IF(Client.sex = 2 AND age(Client.birthDate, Action.endDate) < 55, Action.id, NULL)) AS countWomen55
                      , COUNT(IF(Client.sex = 2 AND age(Client.birthDate, Action.endDate) > 55, Action.id, NULL)) AS countWomenAfter55
                      , COUNT(IF(DATEDIFF(Action.endDate, Client.birthDate) < 7, Action.id, NULL)) AS countChildren6days
                      , COUNT(IF(DATEDIFF(Action.endDate, Client.birthDate) >= 7 AND DATEDIFF(Action.endDate, Client.birthDate) < 29, Action.id, NULL)) AS countChildren28days
                      , COUNT(IF(age(Client.birthDate, Action.endDate) < 1, Action.id, NULL)) AS countChildrenYear
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 1 AND age(Client.birthDate, Action.endDate) < 4, Action.id, NULL)) AS countChildren3year
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 4 AND age(Client.birthDate, Action.endDate) < 7, Action.id, NULL)) AS countChildren6year
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 7 AND age(Client.birthDate, Action.endDate) < 15, Action.id, NULL)) AS countChildren14year
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 15 AND age(Client.birthDate, Action.endDate) < 18, Action.id, NULL)) AS countTeenager
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 18 AND age(Client.birthDate, Action.endDate) < 20, Action.id, NULL)) AS countAdult18
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 20 AND age(Client.birthDate, Action.endDate) < 30, Action.id, NULL)) AS countAdult20
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 30 AND age(Client.birthDate, Action.endDate) < 40, Action.id, NULL)) AS countAdult30
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 40 AND age(Client.birthDate, Action.endDate) < 50, Action.id, NULL)) AS countAdult40
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 50 AND age(Client.birthDate, Action.endDate) < 60, Action.id, NULL)) AS countAdult50
                      , COUNT(IF(age(Client.birthDate, Action.endDate) >= 60 AND age(Client.birthDate, Action.endDate) < 70, Action.id, NULL)) AS countAdult60
                      , COUNT(IF(age(Client.birthDate, Action.endDate) > 70, Action.id, NULL)) AS countAdult70
               FROM Action
                  INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.flatCode = 'leaved' AND  Action.deleted = 0
                  INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
                  INNER JOIN Client ON Client.id = Event.client_id
                  INNER JOIN Action act ON act.id = (SELECT MAX(a.id)
                                                     FROM ActionType at
                                                     INNER JOIN Action a ON a.actionType_id = at.id AND a.deleted = 0
                                                     WHERE at.flatCode = 'moving' AND a.event_id = Event.id AND at.deleted = 0)
                  INNER JOIN ActionProperty ON ActionProperty.action_id = act.id
                  AND ActionProperty.type_id = (SELECT apt.id
                                                  FROM ActionPropertyType apt
                                                  INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'moving' AND at.deleted = 0
                                                  WHERE apt.name = 'Отделение пребывания' AND apt.deleted = 0) AND ActionProperty.deleted = 0
                  INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                  INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                  LEFT JOIN ActionProperty apHospitalBedProfile ON apHospitalBedProfile.action_id = act.id AND apHospitalBedProfile.type_id = (SELECT apt.id
                                                                                                                                                FROM ActionPropertyType apt
                                                                                                                                                INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'moving' AND at.deleted = 0
                                                                                                                                                WHERE apt.name = 'Профиль') AND apHospitalBedProfile.deleted = 0
                  LEFT JOIN ActionProperty_rbHospitalBedProfile aphb ON aphb.id = apHospitalBedProfile.id
                  LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = aphb.value
                  LEFT JOIN Action act_received ON act_received.event_id = Event.id AND act_received.actionType_id = (SELECT at.id
                                                                                                                      FROM ActionType at
                                                                                                                      WHERE at.flatCode = 'received' AND at.deleted = 0) AND act_received.deleted = 0
                  LEFT JOIN ActionProperty ap ON ap.action_id = act_received.id AND ap.type_id = (SELECT apt.id
                                                                                                    FROM ActionPropertyType apt
                                                                                                    INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND at.deleted = 0
                                                                                                    WHERE apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0)
                  LEFT JOIN ActionProperty_String aps ON aps.id = ap.id
               WHERE %s
               GROUP BY %s
               ORDER BY %s''' % (db.joinAnd(cond), ','.join(group), ','.join(order))
    return db.query(stmt)

class CReportAgeSexCompositionLeavedClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Справка о возростно-половом составе выбывших из стационара')

    def getSetupDialog(self, parent):
        result = CAgeSexCompositionLeavedClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        ungroupProfileBed = params.get('ungroupProfileBed')
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ( '20%', [u'Отделение'                ], CReportBase.AlignCenter),
            ( '20%', [u'Профиль'                  ], CReportBase.AlignCenter),
            ( '3%',  [u'Всего выбыв'              ], CReportBase.AlignRight),
            ( '3%',  [u'М',           u'Всего'    ], CReportBase.AlignRight),
            ( '3%',  [u'',            u'до 60'    ], CReportBase.AlignRight),
            ( '3%',  [u'',            u'ст 60'    ], CReportBase.AlignRight),
            ( '3%',  [u'Ж',           u'Всего'    ], CReportBase.AlignRight),
            ( '3%',  [u'',            u'до 55'    ], CReportBase.AlignRight),
            ( '3%',  [u'',            u'ст 55'    ], CReportBase.AlignRight),
            ( '10%', [u'Дети',        u'0-6 дней' ], CReportBase.AlignRight),
            ( '10%', [u'',            u'7-28 дней'], CReportBase.AlignRight),
            ( '10%', [u'',            u'до года'  ], CReportBase.AlignRight),
            ( '10%', [u'',            u'1-3 года' ], CReportBase.AlignRight),
            ( '10%', [u'',            u'4-6 лет'  ], CReportBase.AlignRight),
            ( '10%', [u'',            u'7-14 лет' ], CReportBase.AlignRight),
            ( '10%', [u'Подр',        u'15-17'    ], CReportBase.AlignRight),
            ( '10%', [u'Взрослые',    u'18-19'    ], CReportBase.AlignRight),
            ( '10%', [u'',            u'20-29'    ], CReportBase.AlignRight),
            ( '10%', [u'',            u'30-39'    ], CReportBase.AlignRight),
            ( '10%', [u'',            u'40-49'    ], CReportBase.AlignRight),
            ( '10%', [u'',            u'50-59'    ], CReportBase.AlignRight),
            ( '10%', [u'',            u'60-69'    ], CReportBase.AlignRight),
            ( '10%', [u'',            u'ст.70'    ], CReportBase.AlignRight)]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0,  2, 1)
        table.mergeCells(0, 1,  2, 1)
        table.mergeCells(0, 2,  2, 1)
        table.mergeCells(0, 3,  1, 3)
        table.mergeCells(0, 6,  1, 3)
        table.mergeCells(0, 9,  1, 6)
        table.mergeCells(0, 16, 1, 7)

        total = [0] * 21
        commonTotal = [0] * 21
        currentOrgStructure = None
        currentHospitalBedProfile = None
        rowsHospitalBedPlofile = 0
        while query.next():
            record = query.record()
            code               = forceString(record.value('code'))
            name                = forceString(record.value('name')).strip()
            countEvent          = forceInt(record.value('countEvent'))
            countMen            = forceInt(record.value('countMen'))
            countMen60          = forceInt(record.value('countMen60'))
            countMenAfter60     = forceInt(record.value('countMenAfter60'))
            countWomen          = forceInt(record.value('countWomen'))
            countWomen55        = forceInt(record.value('countWomen55'))
            countWomenAfter55   = forceInt(record.value('countWomenAfter55'))
            countChildren6days  = forceInt(record.value('countChildren6days'))
            countChildren28days = forceInt(record.value('countChildren28days'))
            countChildrenYear   = forceInt(record.value('countChildrenYear'))
            countChildren3year  = forceInt(record.value('countChildren3year'))
            countChildren6year  = forceInt(record.value('countChildren6year'))
            countChildren14year = forceInt(record.value('countChildren14year'))
            countTeenager       = forceInt(record.value('countTeenager'))
            countAdult18        = forceInt(record.value('countAdult18'))
            countAdult20        = forceInt(record.value('countAdult20'))
            countAdult30        = forceInt(record.value('countAdult30'))
            countAdult40        = forceInt(record.value('countAdult40'))
            countAdult50        = forceInt(record.value('countAdult50'))
            countAdult60        = forceInt(record.value('countAdult60'))
            countAdult70        = forceInt(record.value('countAdult70'))
            if not ungroupProfileBed:
                if currentOrgStructure is None or currentOrgStructure != code:
                    if rowsHospitalBedPlofile:
                        i = table.addRow()
                        table.setText(i, 1, u'Итого',  CReportBase.TableTotal)
                        for column, value in enumerate(total):
                            commonTotal[column] += value
                            table.setText(i, column + 2, value, CReportBase.TableTotal)
                        total = [0] * 21
                    i = table.addRow()
                    table.setText(i, 0, code)
                    table.mergeCells(i - rowsHospitalBedPlofile - 1, 0, rowsHospitalBedPlofile + 1, 1)
                    currentOrgStructure = code
                    rowsHospitalBedPlofile = 0
                if currentHospitalBedProfile is None or currentHospitalBedProfile != name or not rowsHospitalBedPlofile:
                    if rowsHospitalBedPlofile:
                        i = table.addRow()
                    table.setText(i, 1, name)
                    currentHospitalBedProfile = name
            else:
                i = table.addRow()
                table.setText(i, 0, code)
                table.setText(i, 1, u'Итого')
            table.setText(i, 2,  countEvent)
            table.setText(i, 3,  countMen)
            table.setText(i, 4,  countMen60)
            table.setText(i, 5,  countMenAfter60)
            table.setText(i, 6,  countWomen)
            table.setText(i, 7,  countWomen55)
            table.setText(i, 8,  countWomenAfter55)
            table.setText(i, 9,  countChildren6days)
            table.setText(i, 10, countChildren28days)
            table.setText(i, 11, countChildrenYear)
            table.setText(i, 12, countChildren3year)
            table.setText(i, 13, countChildren6year)
            table.setText(i, 14, countChildren14year)
            table.setText(i, 15, countTeenager)
            table.setText(i, 16, countAdult18)
            table.setText(i, 17, countAdult20)
            table.setText(i, 18, countAdult30)
            table.setText(i, 19, countAdult40)
            table.setText(i, 20, countAdult50)
            table.setText(i, 21, countAdult60)
            table.setText(i, 22, countAdult70)
            total[0]  += countEvent
            total[1]  += countMen
            total[2]  += countMen60
            total[3]  += countMenAfter60
            total[4]  += countWomen
            total[5]  += countWomen55
            total[6]  += countWomenAfter55
            total[7]  += countChildren6days
            total[8]  += countChildren28days
            total[9]  += countChildrenYear
            total[10] += countChildren3year
            total[11] += countChildren6year
            total[12] += countChildren14year
            total[13] += countTeenager
            total[14] += countAdult18
            total[15] += countAdult20
            total[16] += countAdult30
            total[17] += countAdult40
            total[18] += countAdult50
            total[19] += countAdult60
            total[20] += countAdult70

            rowsHospitalBedPlofile += 1
        if not ungroupProfileBed:
            i = table.addRow()
            table.setText(i, 1, u'Итого',  CReportBase.TableTotal)
            for column, value in enumerate(total):
                table.setText(i, column + 2, value, CReportBase.TableTotal)
            for column, value in enumerate(total):
                commonTotal[column] += value
            table.mergeCells(i - rowsHospitalBedPlofile, 0, rowsHospitalBedPlofile + 1, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(commonTotal if not ungroupProfileBed else total):
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        return doc

class CAgeSexCompositionLeavedClients(QtGui.QDialog, Ui_ReportAgeSexCompositionLeavedClients):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbProfileBed.setTable('rbHospitalBedProfile', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbProfileBed.setValue(params.get('profileBed', None))
        self.cmbOrder.setCurrentIndex(params.get('order', 0))
        self.cmbTypeHosp.setCurrentIndex(params.get('typeHosp', 0))
        self.chkUngroupProfileBeds.setChecked(params.get('ungroupProfileBed', False))

    def params(self):
        params = {}
        params['begDate']           = self.edtBegDate.date()
        params['endDate']           = self.edtEndDate.date()
        params['orgStructureId']    = self.cmbOrgStructure.value()
        params['profileBed']        = self.cmbProfileBed.value()
        params['order']             = self.cmbOrder.currentIndex()
        params['typeHosp']          = self.cmbTypeHosp.currentIndex()
        params['ungroupProfileBed'] = self.chkUngroupProfileBeds.isChecked()
        return params