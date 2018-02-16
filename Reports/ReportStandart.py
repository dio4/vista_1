# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.Utils                              import forceDouble, forceInt, forceString
from Orgs.Utils                                 import getOrgStructureDescendants
from Reports.Report                             import CReport
from Reports.ReportBase                         import createTable, CReportBase

from Ui_ReportStandart import Ui_ReportStandart

def selectData(params, lstStandart):
    db = QtGui.qApp.db

    begDate        = params.get('begDate')
    endDate        = params.get('endDate')
    typeHosp       = params.get('typeHosp')
    mesId          = params.get('mesId')
    insurerId      = params.get('insurerId')
    orgStructureId = params.get('orgStructureId')
    personId       = params.get('personId')
    cmbStandart = params.get('cmbStandart')

    tableEvent  = db.table('Event')
    tableAction = db.table('Action')
    tableClientPolicyCompulsory = db.table('ClientPolicy').alias('cpCompulsory')
    tableClientPolicy = db.table('ClientPolicy')
    tableOrgStructure = db.table('OrgStructure')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableMes = db.table('mes.MES').alias('mes')

    cond = ['IF(Event.MES_id, %s, %s)' %(db.joinAnd([tableEvent['execDate'].dateGe(begDate), tableEvent['execDate'].dateLe(endDate)]), db.joinAnd([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].dateLe(endDate)]))]

    if lstStandart and cmbStandart:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableMes['id'].inlist(lstStandart))
    if mesId and not cmbStandart:
        cond.append(tableMes['id'].eq(mesId))
    if insurerId:
        cond.append(db.joinOr([tableClientPolicyCompulsory['insurer_id'].eq(insurerId), tableClientPolicy['insurer_id'].eq(insurerId)]))
    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if typeHosp == 1:
        cond.extend([u'OrgStructure.hasDayStationary = 0', 'OrgStructure.type != 4'])
    elif typeHosp == 2:
        cond.append(u'OrgStructure.hasDayStationary = 1')

    stmt = u'''SELECT CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientInfo,
                    mes.code,
                    IF(Event.MES_id, CONCAT(DATE_FORMAT(Event.setDate, '%%d.%%m.%%Y'), '/', DATE_FORMAT(Event.execDate,'%%d.%%m.%%Y')), CONCAT(DATE_FORMAT(Action.begDate, '%%d.%%m.%%Y'), '/', DATE_FORMAT(Action.endDate, '%%d.%%m.%%Y'))) AS dates,
                    @a:=IF(Event.MES_id, IF(Event.execDate IS NOT NULL, datediff(Event.execDate, Event.setDate), datediff(CURDATE(), Event.setDate)), IF(Action.endDate IS NOT NULL, DATEDIFF(Action.endDate, Action.begDate), DATEDIFF(CURDATE(), Action.begDate))) AS tmpDuration,
                    if(OrgStructure.hasDayStationary = 1, @a:=@a+1, @a) as duration,
                    vrbPersonWithSpeciality.name,
                    @a * Contract_Tariff.price AS tariff

            FROM Event
                INNER JOIN Client ON Client.id = Event.client_id
                LEFT JOIN Action ON Action.event_id = Event.id AND Action.actionType_id = (SELECT AT.id
                                                                                            FROM ActionType AT
                                                                                            WHERE AT.flatCode = 'moving' AND AT.deleted = 0) AND Action.deleted = 0
                LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = Action.actionType_id AND ActionPropertyType.name = 'Отделение пребывания' AND ActionPropertyType.deleted = 0
                LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                INNER JOIN mes.MES mes ON mes.id = IF(Event.MES_id, Event.MES_id, Action.MES_id)
                INNER JOIN rbService ON rbService.code = mes.code
                INNER JOIN Contract_Tariff  ON Contract_Tariff.service_id = rbService.id AND Contract_Tariff.master_id = IF(Action.contract_id,  Action.contract_id, Event.contract_id) AND (DATE(Contract_Tariff.begDate) <= IF(Event.MES_id, DATE(Event.execDate), DATE(Action.endDate)) OR Contract_Tariff.begDate IS NULL) AND (DATE(Contract_Tariff.endDate) >= IF(Event.MES_id, DATE(Event.execDate), DATE(Action.endDate)) OR Contract_Tariff.endDate IS NULL)
                LEFT JOIN ClientPolicy cpCompulsory ON cpCompulsory.client_id = Client.id AND cpCompulsory.id = getClientPolicyOnDateId(Client.id, 1, Event.setDate)
                LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.id = getClientPolicyOnDateId(Client.id, 0, Event.setDate)
                LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = IF(Event.MES_id, Event.execPerson_id, Action.person_id)
            WHERE %s AND Event.deleted = 0
            ORDER BY clientInfo, dates, code, name''' % (db.joinAnd(cond))

    return db.query(stmt)

class CReportStandart(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по стандартам')

    def getSetupDialog(self, parent):
        dialog = CStandart(parent)
        dialog.setTitle(self.title())
        return dialog

    def build(self, params):
        lstStandartDict = params.get('lstStandart', None)
        lstStandart = lstStandartDict.keys()
        query = selectData(params, lstStandart)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('20?', [u'ФИО пациента'         ], CReportBase.AlignLeft),
                        ('15?', [u'Код стандарта'        ], CReportBase.AlignCenter),
                        ('10?', [u'Даты начала/окончания'], CReportBase.AlignLeft),
                        ('5?',  [u'К/д'                  ], CReportBase.AlignCenter),
                        ('15?', [u'ФИО врача'            ], CReportBase.AlignLeft),
                        ('5?',  [u'Сумма'                ], CReportBase.AlignCenter)
                        ]

        table = createTable(cursor, tableColumns)

        currentClient = None
        countStandart = 0
        while query.next():
            record = query.record()
            client = forceString(record.value('clientInfo'))
            standart = forceString(record.value('code'))
            dates = forceString(record.value('dates'))
            duration = forceInt(record.value('duration'))
            person = forceString(record.value('name'))
            tariff = forceDouble(record.value('tariff'))

            i = table.addRow()
            if client != currentClient:
                if currentClient is not None:
                    table.mergeCells(i - countStandart, 0, countStandart, 1)
                    countStandart = 0
                table.setText(i, 0, client)
                currentClient = client

            table.setText(i, 1, standart)
            table.setText(i, 2, dates)
            table.setText(i, 3, duration)
            table.setText(i, 4, person)
            table.setText(i, 5, tariff)

            countStandart += 1

        if countStandart > 1:
            table.mergeCells(i - countStandart, 0, countStandart, 1)

        return doc

class CStandart(QtGui.QDialog, Ui_ReportStandart):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstStandart.setTable('mes.MES')
        self.lstStandart.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbHospitalization.setCurrentIndex(params.get('typeHosp', 0))
        self.cmbStandart.setValue(params.get('mesId', None))
        self.cmbInsurerFilterDialog.setValue(params.get('insurerId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['typeHosp'] = self.cmbHospitalization.currentIndex()
        params['mesId'] = self.cmbStandart.value()
        params['insurerId'] = self.cmbInsurerFilterDialog.value()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['personId'] = self.cmbPerson.value()
        params['lstStandart'] = self.lstStandart.nameValues()
        params['cmbStandart'] = self.chkStandart.isChecked()
        return params

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(bool)
    def on_chkStandart_clicked(self, checked):
        self.lstStandart.setVisible(checked)
        self.cmbStandart.setVisible(not checked)