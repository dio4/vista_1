# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportF16           import Ui_ReportF16


def selectData(params, lstOrgStructure, lstProfileBed):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    order           = params.get('order')
    orgStructureId  = params.get('orgStructureId')
    typeHosp        = params.get('typeHosp')
    cmbOrgStructure = params.get('cmbOrgStructure')
    cmbProfileBed   = params.get('cmbProfileBed')
    profileBed      = params.get('profileBed')
    financeId       = params.get('financeId')

    typeSubQuery = {'moving'         : ('moving',      u'Отделение пребывания'),
                    'received'       : ('received',    u'Направлен в отделение'),
                    'movingInto'     : ('moving',      u'Переведен в отделение'),
                    'movingFrom'     : ('moving',      u'Переведен из отделения'),
                    'leaved'         : ('leaved',      None)}

    def subQuery(typeQuery):
        infoTypeQuery = typeSubQuery[typeQuery]
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableActionPropertyType = db.table('ActionPropertyType')
        tableActionProperty = db.table('ActionProperty')
        tableAPOrgStructure = db.table('ActionProperty_OrgStructure')
        tableOrgStructure = db.table('OrgStructure')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableHospitalBedProfile = db.table('rbHospitalBedProfile')
        tableAPHospitalBed = db.table('ActionProperty').alias('apHospitalBedProfile')
        tableAPHospitalBedProfile = db.table('ActionProperty_rbHospitalBedProfile')
        tableClientAddress = db.table('ClientAddress')

        select = []

        queryTable = tableActionType.innerJoin(tableAction, [tableAction['actionType_id'].eq(tableActionType['id']),
                                                             tableAction['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableEvent, [tableEvent['id'].eq(tableAction['event_id']),
                                                           tableEvent['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

        if infoTypeQuery[1] is not None:
            select.append('COUNT(%s) %s' % (tableAction['id'], typeQuery))
            queryTable = queryTable.innerJoin(tableActionPropertyType, [tableActionPropertyType['actionType_id'].eq(tableActionType['id']),
                                                                        tableActionPropertyType['name'].eq(infoTypeQuery[1]),
                                                                        tableActionPropertyType['deleted'].eq(0)])
            queryTable = queryTable.innerJoin(tableActionProperty, [tableActionProperty['action_id'].eq(tableAction['id']),
                                                                    tableActionProperty['type_id'].eq(tableActionPropertyType['id']),
                                                                    tableActionProperty['deleted'].eq(0)])
        tableMoving = tableAction
        if typeQuery in ('received', 'leaved'):
            tableActMoving = db.table('Action').alias('act_moving')
            queryTable = queryTable.innerJoin(tableActMoving, u'''act_moving.id = (SELECT %s
                                                                  FROM ActionType at
                                                                    INNER JOIN Action a ON a.actionType_id = at.id AND a.deleted = 0
                                                                  WHERE at.flatCode = 'moving' AND a.event_id = Event.id AND at.deleted = 0)''' % ('MAX(a.id)' if typeQuery == 'leaved' else 'MIN(a.id)'))
            tableMoving = tableActMoving
        queryTable = queryTable.leftJoin(tableAPHospitalBed, [tableAPHospitalBed['action_id'].eq(tableMoving['id']),
                                                              u'''apHospitalBedProfile.type_id = (SELECT apt.id
                                                                                                  FROM ActionPropertyType apt
                                                                                                  INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'moving' AND at.deleted = 0
                                                                                                  WHERE apt.name = 'Профиль койки') AND apHospitalBedProfile.deleted = 0 '''])
        queryTable = queryTable.leftJoin(tableAPHospitalBedProfile, tableAPHospitalBedProfile['id'].eq(tableAPHospitalBed['id']))
        queryTable = queryTable.leftJoin(tableHospitalBedProfile, tableHospitalBedProfile['id'].eq(tableAPHospitalBedProfile['value']))

        select.extend([tableHospitalBedProfile['id'].alias('hbpId'),
                       tableAPOrgStructure['value'].alias('id')])

        if typeQuery != 'leaved':
            queryTable = queryTable.innerJoin(tableAPOrgStructure, tableAPOrgStructure['id'].eq(tableActionProperty['id']))

        cond = [tableActionType['flatCode'].eq(infoTypeQuery[0])]
        if order:
            cond.append(tableEvent['order'].eq(order))
        if lstOrgStructure and cmbOrgStructure:
            cond.append(tableAPOrgStructure['value'].inlist(lstOrgStructure))
        if orgStructureId and not cmbOrgStructure:
            cond.append(tableAPOrgStructure['value'].inlist(getOrgStructureDescendants(orgStructureId)))
        if lstProfileBed and cmbProfileBed:
            cond.append(tableHospitalBedProfile['id'].inlist(lstProfileBed))
        if profileBed:
            cond.append(tableHospitalBedProfile['id'].eq(profileBed))
        tableAct = db.table('Action').alias('act')
        tableAp = db.table('ActionProperty').alias('ap')
        tableAPS = db.table('ActionProperty_String').alias('aps')
        queryTable = queryTable.leftJoin(tableAct, [tableAct['event_id'].eq(tableEvent['id']),
                                                     tableAct['actionType_id'].eq(db.translate('ActionType', 'flatCode', 'received', 'id'))])
        queryTable = queryTable.leftJoin(tableAp, [tableAp['action_id'].eq(tableAct['id']),
                                                    u'''ap.type_id = (SELECT apt.id
                                                                      FROM ActionPropertyType apt
                                                                      WHERE apt.actionType_id = act.actionType_id AND apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0)'''])
        queryTable = queryTable.leftJoin(tableAPS, tableAPS['id'].eq(tableAp['id']))
        if typeHosp == 1:
            cond.extend([u'OrgStructure.code NOT LIKE \'Д/С%\'', 'aps.value IS NULL'])
        if typeHosp == 3:
            cond.append('aps.value IS NOT NULL')
        if financeId:
            cond.append(tableAction['finance_id'].eq(financeId))

        group = [tableAPOrgStructure['value'],
                 tableAPHospitalBedProfile['value']]

        if typeQuery == 'received':
            select.append(u'''COUNT(if(ClientAddress.isVillager = 1 OR isClientVillager(Client.id) = 1, ActionProperty.id, NULL)) AS receivedVillager
                            , COUNT(if(age(Client.birthDate, Action.begDate) <= 17, ActionProperty.id, NULL)) AS receivedChildren
                            , COUNT(if(age(Client.birthDate, Action.begDate) >= 60, ActionProperty.id, NULL)) AS receivedPensioner
                            , COUNT(if(Event.order = 2, Action.id, NULL)) AS extra''')
                            #, sum(if(Date(Event.execDate) > Date(%s), datediff(DATE(%s), Event.setDate), datediff(Event.execDate, Event.setDate)) AS duration''' % (endDate, endDate))

            cond.extend([tableAction['begDate'].dateGe(begDate), tableAction['begDate'].dateLe(endDate)])
            queryTable = queryTable.innerJoin(tableClientAddress, tableClient['id'].eq(tableClientAddress['client_id']))
        elif typeQuery == 'moving':
            #select.append('sum(if(Date(Event.execDate) > Date(%s), datediff(DATE(%s), DATE(%s)), datediff(Event.execDate, DATE(%s))) AS duration' % (endDate, endDate, begDate, begDate))
            cond.extend([tableAction['begDate'].dateLt(begDate),
                         db.joinOr([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].isNull()])])
        elif typeQuery == 'movingInto':
            #select.append('sum(if(Date(Event.execDate) > Date(%s), datediff(DATE(%s), DATE(%s)), datediff(Event.execDate, DATE(%s))) AS duration' % (endDate, endDate, begDate, begDate))
            cond.extend([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].dateLe(endDate)])
        elif typeQuery == 'movingFrom':
            cond.extend([tableAction['begDate'].dateGe(begDate), tableAction['begDate'].dateLe(endDate)])
        else:
            tableActionPropertyResult = db.table('ActionProperty').alias('ActionPropertyResult')
            tableActionPropertyTypeResult = db.table('ActionPropertyType').alias('ActionPropertyTypeResult')

            tableAPString = db.table('ActionProperty_String')
            tableAPOS = db.table('ActionProperty').alias('ap_os')
            select.append(u'''COUNT(ap_os.id) AS leaved
                            , COUNT(IF(ActionProperty_String.value = 'умер', ActionProperty_String.id, NULL)) AS leavedDeath
                            , COUNT(IF(ActionProperty_String.value = 'переведен в другой стационар', ActionProperty_String.id, NULL)) AS leavedOther
                            , COUNT(IF(ActionProperty_String.value = 'выписан в дневной стационар', ActionProperty_String.id, NULL)) AS leavedSt''')
            queryTable = queryTable.innerJoin(tableAPOS, [tableAPOS['action_id'].eq(tableMoving['id']),
                                                          u'''ap_os.type_id = (SELECT apt.id
                                                                               FROM ActionPropertyType apt
                                                                               WHERE apt.actionType_id = act_moving.actionType_id AND apt.name = 'Отделение пребывания' AND apt.deleted = 0) AND ap_os.deleted = 0'''])
            queryTable = queryTable.innerJoin(tableAPOrgStructure, tableAPOrgStructure['id'].eq(tableAPOS['id']))
            queryTable = queryTable.leftJoin(tableActionPropertyTypeResult, [tableActionPropertyTypeResult['actionType_id'].eq(tableActionType['id']),
                                                                             tableActionPropertyTypeResult['name'].eq(u'Исход госпитализации'),
                                                                             tableActionPropertyTypeResult['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableActionPropertyResult, [tableActionPropertyResult['action_id'].eq(tableAction['id']),
                                                                         tableActionPropertyResult['type_id'].eq(tableActionPropertyTypeResult['id']),
                                                                         tableActionPropertyResult['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableAPString, tableAPString['id'].eq(tableActionPropertyResult['id']))
            cond.extend([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].dateLe(endDate)])
        queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableAPOrgStructure['value']))
        return db.selectStmt(queryTable, select, cond, group)

    cond = []
    if typeHosp == 2:
        cond.append(u'mainTable.code LIKE \'Д/С%\'')

    stmt = ''' SELECT  mainTable.code,
                       rbHospitalBedProfile.name,
                       received.receivedVillager,
                       received.receivedChildren,
                       received.receivedPensioner,
                       moving.moving,
                       leaved.leavedOther,
                       leaved.leavedSt,
                       received.received,
                       leaved.leaved,
                       leaved.leavedDeath,
                       movingInto.movingInto,
                       movingFrom.movingFrom,
                       received.extra
                FROM OrgStructure AS mainTable
                JOIN rbHospitalBedProfile
                LEFT JOIN (%s) received ON received.id = mainTable.id AND rbHospitalBedProfile.id = received.hbpId
                LEFT JOIN (%s) movingInto ON movingInto.id = mainTable.id AND rbHospitalBedProfile.id = movingInto.hbpId
                LEFT JOIN (%s) movingFrom ON movingFrom.id = mainTable.id AND rbHospitalBedProfile.id = movingFrom.hbpId
                LEFT JOIN (%s) leaved ON leaved.id = mainTable.id AND rbHospitalBedProfile.id = leaved.hbpId
                LEFT JOIN (%s) moving ON moving.id = mainTable.id AND rbHospitalBedProfile.id = moving.hbpId
                WHERE (received.received OR moving.moving OR leaved.leaved OR movingInto.movingInto OR movingFrom.movingFrom) %s
                GROUP BY mainTable.id, rbHospitalBedProfile.id''' % (subQuery('received'),
                                                            subQuery('movingInto'),
                                                            subQuery('movingFrom'),
                                                            subQuery('leaved'),
                                                            subQuery('moving'), 'AND %s' % db.joinAnd(cond) if cond else '')
    return db.query(stmt)

class CReportF16(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сводная ведомость учета движения больных и коечного фонда по стационару (Ф - 16)')

    def getSetupDialog(self, parent):
        result = CF16(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        lstProfileBedDict = params.get('lstProfileBed', None)
        lstProfileBed = lstProfileBedDict.keys()
        query = selectData(params, lstOrgStructure, lstProfileBed)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Отделение'                                           ], CReportBase.AlignLeft),
            ('20%',  [u'Профиль'                                             ], CReportBase.AlignLeft),
            (' 3%',  [u'Число коек',             u'всего развернутых'        ], CReportBase.AlignRight),
            (' 3%',  [u'',                       u'в т.ч. сверн. на ремонт'  ], CReportBase.AlignRight),
            (' 3%',  [u'Среднемесячн. коек'                                  ], CReportBase.AlignRight),
            (' 3%',  [u'Состояло на начало'                                  ], CReportBase.AlignRight),
            (' 3%',  [u'За отчетный период', u'Поступило',  u'Всего'         ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'Из дн стац'    ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'Сельских'      ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'0-17'          ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'60 лет и более'], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'Переведено', u'Из др. отд.'   ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'В др.отд.'     ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'Выписано',   u'Всего'         ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'Днев.стац.'    ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'',           u'Др.стац.'      ], CReportBase.AlignRight),
            (' 3%',  [u'',                   u'Умерло',                      ], CReportBase.AlignRight),
            (' 3%',  [u'Состоит на конец'                                    ], CReportBase.AlignRight),
            ('10%',  [u'Проведено больными койко-дней'                       ], CReportBase.AlignRight),
            ('10%',  [u'Кроме того:',        u'Число койко-дней закрытия'    ], CReportBase.AlignRight),
            ('10%',  [u'',                   u'Проведено койко-дней по уходу'], CReportBase.AlignRight),
            ('10%',  [u'Поступило экстренных больных'                        ], CReportBase.AlignRight)]
        table = createTable(cursor, tableColumns)

        countColumns = len(tableColumns)

        table.mergeCells(0,  0, 3,  1)
        table.mergeCells(0,  1, 3,  1)
        table.mergeCells(0,  2, 1,  2)
        table.mergeCells(1,  2, 2,  1)
        table.mergeCells(1,  3, 2,  1)
        table.mergeCells(0,  4, 3,  1)
        table.mergeCells(0,  5, 3,  1)
        table.mergeCells(0,  6, 1, 11)
        table.mergeCells(1,  6, 1,  5)
        table.mergeCells(1, 11, 1,  2)
        table.mergeCells(1, 13, 1,  3)
        table.mergeCells(1, 16, 2,  1)
        table.mergeCells(0, 17, 3,  1)
        table.mergeCells(0, 18, 3,  1)
        table.mergeCells(0, 19, 1,  2)
        table.mergeCells(1, 19, 2,  1)
        table.mergeCells(1, 20, 2,  1)
        table.mergeCells(0, 21, 3,  1)

        currentOrgStructure = None
        countHospitalBed = 0
        totalOrgStructure = [0] * (countColumns - 2)
        total = totalOrgStructure
        while query.next():
            record = query.record()
            orgStructure = forceString(record.value('code'))
            hospilatBed  = forceString(record.value('name'))
            permanent = forceInt(record.value('permanent'))
            involution = forceInt(record.value('involution'))
            receivedVillager = forceInt(record.value('receivedVillager'))
            receivedChildren = forceInt(record.value('receivedChildren'))
            receivedPensioner = forceInt(record.value('receivedPensioner'))
            duration = forceInt(record.value('duration'))
            moving = forceInt(record.value('moving'))
            leavedOther = forceInt(record.value('leavedOther'))
            leavedSt = forceInt(record.value('leavedSt'))
            received = forceInt(record.value('received'))
            leaved = forceInt(record.value('leaved'))
            leavedDeath = forceInt(record.value('leavedDeath'))
            movingInto = forceInt(record.value('movingInto'))
            movingFrom = forceInt(record.value('movingFrom'))
            extra = forceInt(record.value('extra'))
            i = table.addRow()
            if currentOrgStructure != orgStructure:
                if currentOrgStructure is not None:
                    table.setText(i, 1, u'Итого', CReportBase.TableTotal)
                    for column, value in enumerate(totalOrgStructure):
                        total[column] += value
                        table.setText(i, column + 2, value, CReportBase.TableTotal)
                    table.mergeCells(i - countHospitalBed, 0, countHospitalBed + 1, 1)
                    i = table.addRow()
                totalOrgStructure = [0] * (countColumns - 2)
                table.setText(i, 0, orgStructure)
                currentOrgStructure = orgStructure
                countHospitalBed = 0
            table.setText(i,  1, hospilatBed)
            table.setText(i,  2, permanent)
            table.setText(i,  3, involution)
            table.setText(i,  4, permanent - involution)
            table.setText(i,  5, moving)
            table.setText(i,  6, received)
            table.setText(i,  8, receivedVillager)
            table.setText(i,  9, receivedChildren)
            table.setText(i, 10, receivedPensioner)
            table.setText(i, 11, movingInto)
            table.setText(i, 12, movingFrom)
            table.setText(i, 13, leaved)
            table.setText(i, 14, leavedSt)
            table.setText(i, 15, leavedOther)
            table.setText(i, 16, leavedDeath)
            table.setText(i, 17, moving + received - movingFrom + movingInto - leaved - leavedDeath)
            table.setText(i, 19, duration)
            table.setText(i, 21, extra)

            totalOrgStructure[0]  += permanent
            totalOrgStructure[1]  += involution
            totalOrgStructure[2]  += permanent - involution
            totalOrgStructure[3]  += moving
            totalOrgStructure[4]  += received
            totalOrgStructure[6]  += receivedVillager
            totalOrgStructure[7]  += receivedChildren
            totalOrgStructure[8]  += receivedPensioner
            totalOrgStructure[9] += movingInto
            totalOrgStructure[10] += movingFrom
            totalOrgStructure[11] += leaved
            totalOrgStructure[12] += leavedSt
            totalOrgStructure[13] += leavedOther
            totalOrgStructure[14] += leavedDeath
            totalOrgStructure[15] += moving + received - movingFrom + movingInto - leaved - leavedDeath
            totalOrgStructure[16] += duration
            totalOrgStructure[19] += extra
            countHospitalBed += 1
        i = table.addRow()
        table.setText(i, 1, u'Итого', CReportBase.TableTotal)
        for column, value in enumerate(totalOrgStructure):
            total[column] += value
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        table.mergeCells(i - countHospitalBed, 0, countHospitalBed + 1, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(total):
            if column == 2:
                table.setText(i, column + 2, value, CReportBase.TableTotal)
                continue
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        return doc


class CF16(QtGui.QDialog, Ui_ReportF16):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstOrgStructure.setTable('OrgStructure')
        self.lstProfileBed.setTable('rbHospitalBedProfile')
        self.cmbProfileBed.setTable('rbHospitalBedProfile')
        self.cmbFinance.setTable('rbFinance')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbTypeHosp.setCurrentIndex(params.get('typeHosp', 0))
        self.cmbOrder.setCurrentIndex(params.get('order', 0))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbProfileBed.setValue(params.get('profileBed', None))
        self.chkOrgStructure.setChecked(params.get('cmbOrgStructure', False))
        self.chkProfileBed.setChecked(params.get('cmbProfileBed', False))
        self.on_chkOrgStructure_clicked(self.chkOrgStructure.isChecked())
        self.on_chkProfileBed_clicked(self.chkProfileBed.isChecked())

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['typeHosp'] = self.cmbTypeHosp.currentIndex()
        result['order'] = self.cmbOrder.currentIndex()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['profileBed'] = self.cmbProfileBed.value()
        result['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        result['lstProfileBed'] = self.lstProfileBed.nameValues()
        result['cmbProfileBed'] = self.chkProfileBed.isChecked()
        result['cmbOrgStructure'] = self.chkOrgStructure.isChecked()
        result['financeId'] = self.cmbFinance.value()
        return result

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkProfileBed_clicked(self, checked):
        self.lstProfileBed.setVisible(checked)
        self.cmbProfileBed.setVisible(not checked)