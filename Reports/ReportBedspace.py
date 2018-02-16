# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceInt, forceRef, forceString

from Orgs.Utils                         import getOrgStructureDescendants

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.StatReportDDFoundIllnesses import MKBinString

from Ui_ReportBedspace import Ui_ReportBedspace
from Ui_ReportReceivedClients import Ui_ReportReceivedClients


profileBed = {u'ХИМИОТЕРАПЕВТИЧЕСКОЕ (ПЛТ)':[u'Онкологические для взрослых', u''],
              u'РАДИОЛОГИЧЕСКОЕ': [u'', u'Радиологические и рентгенологические'],
              u'НЕЙРОХИРУРГИЧЕСКОЕ': [u'Онкологические для взрослых', u'Нейрохирургические для взрослых'],
              u'КОЛОПРОКТОЛОГИЧЕСКОЕ': [u'Онкологические для взрослых', u'Проктологические для взрослых'],
              u'УРОЛОГИЧЕСКОЕ': [u'Онкоурологические для взрослых', u'Урологические для взрослых'],
              u'ГИНЕКОЛОГИИ': [u'Онкогинекологические для взрослых', u'Гинекологические (кроме коек для производства абортов)'],
              u'ОГиШ': [u'Онкологические опухолей головы и шеи для взрослых', u'Хирургические для взрослых'],
              u'МАММОЛОГИЧЕСКОЕ': [u'Онкологические для взрослых', u'Хирургические для взрослых'],
              u'ТОРАКАЛЬНОЕ': [u'Онкологические тоакальные для взрослых', u'Торакальной хирургии для взрослых'],
              u'ККиМТ': [u'Онкологические опухолей костей, кожи и мягких тканей для взрослых', u'Хирургические для взрослых'],
              u'АБДОМИНАЛЬНОЕ': [u'Онкологические абдоминальные для взрослых', u'Хирургические для взрослых']}

profileBedDC = {u'Д/С Химиотерапии': [u'Койки дневного стационара для взослых - онкологические'],
                u'Радиологическое ДС':   [u'Койки дневного стационара для взослых - радиологические'],
                u'Д/С Нейрохирургии':    [u'Койки дневного стационара для взослых - онкологические'],
                u'Д/С Колопроктологии': [u'Койки дневного стационара для взослых - онкологические'],
                u'Д/С Урологии':        [u'Койки дневного стационара для взослых - онкоурологические'],
                u'Д/С Гинекологии':     [u'Койки дневного стационара для взослых - онкоурологические'],
                u'Д/С ОГиШ':         [u'Койки дневного стационара для взослых - онкологические опухолей головы и шеи'],
                u'Д/С Маммологии':      [u'Койки дневного стационара для взослых - онкологические'],
                u'Д/С Торакальное':          [u'Койки дневного стационара для взослых - онкологические торакальные'],
                u'Д/С ККиМТ':                [u'Койки дневного стационара для взослых - онкологические опухолей костей, кожи и мягких тканей'],
                u'Д/С Абдоминального отделения':        [u'Койки дневного стационара для взослых - онкологические абдоминальные']}

def selectData(begDate, endDate, orgStructureId):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableOrgStructure = db.table('OrgStructure')

    cond = [tableAction['begDate'].dateLe(endDate),
            tableAction['begDate'].dateGe(begDate),
            tableAction['deleted'].eq(0)]

    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    deathResultId = forceRef(db.translate('rbResult', 'code', '06', 'id'))
    daytimeResultId = forceRef(db.translate('rbResult', 'code', '03', 'id'))

    stmt = u'''SELECT OrgStructure.code
                     , Diagnosis.MKB
                     , count(DISTINCT if(OrgStructure_HospitalBed.isPermanent = 1, Action.id, NULL)) AS permanent
                     , count(DISTINCT ReceivedAction.id) AS received
                     , count(DISTINCT if(isClientVillager(Event.client_id), ReceivedAction.id, NULL)) AS receivedVillager
                     , count(DISTINCT if(age(Client.birthDate, Event.setDate) < 17, ReceivedAction.id, NULL)) AS receivedBefore17
                     , count(DISTINCT if(age(Client.birthDate, Event.setDate) > 60, ReceivedAction.id, NULL)) AS receivedAfter60
                     , count(DISTINCT if(MovingActionPropertyType.name = 'Переведен из отделения', MovingActionProperty.id, NULL)) AS movingFrom
                     , count(DISTINCT if(MovingActionPropertyType.name = 'Переведен в отделение', MovingActionProperty.id, NULL)) AS movingInto
                     , count(DISTINCT LeavedAction.id) AS leaved
                     , sum(DISTINCT if(Event.id , datediff(Event.execDate, Event.setDate), NULL)) AS bedDays
                     , count(DISTINCT if(left(AddressHouse.KLADRCode, 2) NOT IN ('78', '47'), Event.id, NULL)) AS nonresident
                     , count(DISTINCT if(Event.order = 2, Event.id, NULL)) AS special
                     , count(DISTINCT if(Event.result_id = %s, Event.id, NULL)) AS death
                     , count(DISTINCT if(Event.result_id = %s, Event.id, NULL)) AS daytimeLeaved
               FROM
                    Action
                    INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.flatCode = 'received'
                    INNER JOIN ActionProperty ON ActionProperty.action_id = Action.id
                    INNER JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id AND ActionPropertyType.name = 'Направлен в отделение'
                    INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                    INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                    INNER JOIN Event ON Event.id = Action.event_id
                    INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
                    INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                    INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code = 7
                    INNER JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.master_id = OrgStructure.id
                    LEFT JOIN Client ON Client.id = Event.client_id
                    LEFT JOIN ClientAddress ON ClientAddress.deleted = 0 AND ClientAddress.id = getClientRegAddress(Event.client_id)
                    LEFT JOIN Address ON Address.deleted = 0 AND Address.id = ClientAddress.address_id
                    LEFT JOIN AddressHouse ON AddressHouse.deleted = 0 AND AddressHouse.id = Address.house_id

                    LEFT JOIN ActionType ReceivedActionType ON ReceivedActionType.deleted = 0 AND ReceivedActionType.flatCode = 'received'
                    LEFT JOIN Action ReceivedAction ON ReceivedAction.event_id = Event.id AND ReceivedAction.actionType_id = ReceivedActionType.id

                    LEFT JOIN ActionType MovingActionType ON MovingActionType.deleted = 0 AND MovingActionType.flatCode = 'moving'
                    LEFT JOIN Action MovingAction ON MovingAction.event_id = Event.id AND MovingAction.actionType_id = MovingActionType.id
                    LEFT JOIN ActionPropertyType MovingActionPropertyType ON ActionPropertyType.name IN ('Переведен из отделения', 'Переведен в отделение')
                    LEFT JOIN ActionProperty MovingActionProperty ON MovingAction.id = MovingActionProperty.action_id AND MovingActionProperty.type_id = MovingActionPropertyType.id

                    LEFT JOIN ActionType LeavedActionType ON LeavedActionType.deleted = 0 AND LeavedActionType.flatCode = 'leaved'
                    LEFT JOIN Action LeavedAction ON LeavedAction.event_id = Event.id AND LeavedAction.actionType_id = LeavedActionType.id

               WHERE
                  Action.deleted = 0
                  AND Event.deleted = 0
                  AND Diagnostic.deleted = 0
                  AND Diagnosis.deleted = 0
                  AND %s
               GROUP BY
                  OrgStructure.id
                , Diagnosis.MKB
                '''
    return db.query(stmt % (deathResultId, daytimeResultId, db.joinAnd(cond)))

def selectDataIsInStationary(begDate, endDate, orgStructureId):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableLeavedAction = db.table('Action').alias('LeavedAction')
    tableOrgStructure = db.table('OrgStructure')

    cond = [tableAction['begDate'].dateLe(endDate),
            tableAction['begDate'].dateGe(begDate),
            tableAction['deleted'].eq(0)]

    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    stmt = u'''SELECT OrgStructure.code
                     , Diagnosis.MKB
                     , count(DISTINCT if(LeavedAction.begDate IS NULL OR %s, LeavedAction.id, NULL)) AS count
                        FROM
                            Action
                            INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.flatCode = 'received'
                            INNER JOIN ActionProperty ON ActionProperty.action_id = Action.id
                            INNER JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id AND ActionPropertyType.name = 'Направлен в отделение'
                            INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                            INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                            INNER JOIN Event ON Event.id = Action.event_id
                            INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
                            INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                            INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code = 7
                            LEFT JOIN ActionType LeavedActionType ON LeavedActionType.deleted = 0 AND LeavedActionType.flatCode = 'leaved'
                            LEFT JOIN Action LeavedAction ON LeavedAction.event_id = Event.id AND LeavedAction.actionType_id = LeavedActionType.id
                        WHERE
                            Action.deleted = 0
                            AND Event.deleted = 0
                            AND Diagnostic.deleted = 0
                            AND Diagnosis.deleted = 0
                            AND %s
               GROUP BY
                  OrgStructure.id
                , Diagnosis.MKB
                '''
    return db.query(stmt % (tableLeavedAction['begDate'].dateGe(endDate), db.joinAnd(cond)))

class CReportBedspace(CReport):
    def __init__(self, parent, daytime = False):
        CReport.__init__(self, parent)
        self.daytime = daytime
        if daytime:
            self.setTitle(u'Коечный фонд ДС')
        else:
            self.setTitle(u'Коечный фонд')

    def getSetupDialog(self, parent):
        result = CBedspace(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate        = params.get('begDate')
        endDate        = params.get('endDate')
        orgStructureId = params.get('orgStructureId')
        queryIsInStationary = selectDataIsInStationary(begDate, endDate, orgStructureId)
        query = selectData(begDate, endDate, orgStructureId)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Профиль'                                          ], CReportBase.AlignLeft),
            ('3%',  [u'Число коек',             u'На конец периода'      ], CReportBase.AlignRight),
            ( '3%', [u'',                       u'Среднеежемесечно'      ], CReportBase.AlignRight),
            ( '3%',  [u'Поступило больных всего'                          ], CReportBase.AlignRight),
            ( '3%',  [u'В том числе',            u'Из дневного стационара'], CReportBase.AlignRight),
            ( '3%',  [u'',                       u'Сельских жителей'      ], CReportBase.AlignRight),
            ( '3%',  [u'',                       u'Детей до 17'           ], CReportBase.AlignRight),
            ( '3%',  [u'',                       u'60 лет и старше'       ], CReportBase.AlignRight),
            ( '10%', [u'Переведено',             u'Из др. отделений      '], CReportBase.AlignRight),
            ( '10%', [u'',                       u'В др.отделения'        ], CReportBase.AlignRight),
            ( '10%', [u'Выписано больных всего', u'Всего'                 ], CReportBase.AlignRight),
            ( '10%', [u'',                       u'В т.ч. дневной стационар'], CReportBase.AlignRight),
            ( '10%', [u'Умерло'                                           ], CReportBase.AlignRight),
            ( '10%', [u'Состоит больных на конец периода'                 ], CReportBase.AlignRight),
            ( '10%', [u'Проведено койко дней'                             ], CReportBase.AlignRight),
            ( '10%', [u'Число койкодней закрытия'                         ], CReportBase.AlignRight),
            ( '10%', [u'Поступило иногородних больных'                    ], CReportBase.AlignRight),
            ( '10%', [u'Поступило экстренных больных'                     ], CReportBase.AlignRight)]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 1, 4)
        table.mergeCells(0, 8, 1, 2)
        table.mergeCells(0, 10, 1, 2)
        table.mergeCells(0, 12, 2, 1)
        table.mergeCells(0, 13, 2, 1)
        table.mergeCells(0, 14, 2, 1)
        table.mergeCells(0, 15, 2, 1)
        table.mergeCells(0, 16, 2, 1)
        table.mergeCells(0, 17, 2, 1)
        table.mergeCells(0, 18, 2, 1)

        self.rowSize = 17
        self.defaultMKB = 'C00.00-D48.9'
        data, total, totalDC = self.processDate(query, queryIsInStationary)

        if not self.daytime:
            i = table.addRow()
            table.setText(i, 0, u'Все койки')
            for index in xrange(len(total)):
                table.setText(i, index + 1, total[index] + totalDC[index])
        i = table.addRow()
        if self.daytime:
            table.setText(i, 0, u'Все койки дневного стационара')
        else:
            table.setText(i, 0, u'Все койки круглосуточного стационара')
        for index in xrange(len(total)):
            table.setText(i, index + 1, total[index])
        # if not self.daytime:
        #     i = table.addRow()
        #     table.setText(i, 0, u'Все койки круглосуточного стационара')
        #     for index in xrange(len(aroundTheClockTotal)):
        #         table.setText(i, index + 1, aroundTheClockTotal[index])
        keys = data.keys()
        keys.sort(key=lambda item: item[0])
        for key in keys:
            i = table.addRow()
            table.setText(i, 0, key)
            for index in xrange(len(data[key])):
                table.setText(i, index + 1, data[key][index])
        return doc


    def createDic(self, nameKeys):
        data = {}
        for key in nameKeys.keys():
            for value in nameKeys[key]:
                if value != u'':
                    data.setdefault(value, [0]*self.rowSize)
        return data

    def totalCount(self, data):
        total = [0]*self.rowSize
        for key in data.keys():
            for index in xrange(len(data[key])):
                value = data[key][index]
                if value:
                    total[index] += value
        return total

    def getRecordIsInStationary(self, query):
        mapValues = {}
        while query.next():
            record = query.record()
            code  = forceString(record.value('code'))
            MKB   = forceString(record.value('MKB'))
            count = forceInt(record.value('count'))
            mapValues[code+' '+MKB] = count
        return mapValues

    def getRecord(self, query, queryIsInStationary):
        listOfData = []
        mapIsInStarionary = self.getRecordIsInStationary(queryIsInStationary)
        while query.next():
            record = query.record()
            code = forceString(record.value('code'))
            MKB  = forceString(record.value('MKB'))
            permanent = forceInt(record.value('permanent'))
            received = forceInt(record.value('received'))
            receivedVillager  = forceInt(record.value('receivedVillager'))
            receivedBefor17 = forceInt(record.value('receivedBefor17'))
            receivedAfter60 = forceInt(record.value('receivedAfter60'))
            movingFrom = forceInt(record.value('movingFrom'))
            movingInto = forceInt(record.value('movingInto'))
            leaved = forceInt(record.value('leaved'))
            bedDays = forceInt(record.value('bedDays'))
            nonresident = forceInt(record.value('nonresident'))
            special = forceInt(record.value('special'))
            death = forceInt(record.value('death'))
            daytimeLeaved = forceInt(record.value('daytimeLeaved'))
            listOfData.append([code, MKB, permanent, permanent, received, 0, receivedVillager, receivedBefor17, receivedAfter60, movingFrom, movingInto, leaved, daytimeLeaved, death, mapIsInStarionary.pop(code + ' ' + MKB, 0), bedDays, 0, nonresident, special])
        if len(mapIsInStarionary):
            for key in mapIsInStarionary.keys():
                values = key.strip().split(' ')
                listOfData.append([0]*19)
                listOfData[len(listOfData)][0] = values[0]
                listOfData[len(listOfData)][1] = values[1]
                listOfData[len(listOfData)][14] = mapIsInStarionary[key]
        return listOfData

    def processDate(self, query, queryIsInStationary):
        totalDC = [0] * self.rowSize
        listOfData = self.getRecord(query, queryIsInStationary)
        if self.daytime:
            data = self.createDic(profileBedDC)
            for index in xrange(len(listOfData)):
                if profileBedDC.get(listOfData[index][0]):
                    key = profileBedDC[listOfData[index][0]][0]
                    for indexValue in xrange(len(listOfData[index]) - 2):
                        data[key][indexValue] += listOfData[index][indexValue + 2]
        else:
            data = self.createDic(profileBed)
            for index in xrange(len(listOfData)):
                codeStructure = listOfData[index][0]
                if codeStructure[:3] == u'Д/С':
                    for indexValue in xrange(len(listOfData[index]) - 2):
                        totalDC[indexValue] += listOfData[index][indexValue + 2]
                    continue
                if profileBed.get(listOfData[index][0]) and MKBinString(listOfData[index][1], self.defaultMKB):
                    key = profileBed[codeStructure][0]
                elif profileBed.get(codeStructure):
                    key = profileBed[codeStructure][1]
                else:
                    key = None
                if key:
                    for indexValue in xrange(len(listOfData[index]) - 2):
                        data[key][indexValue] += listOfData[index][indexValue + 2]
        total = self.totalCount(data)
        return data, total, totalDC


class CBedspace(QtGui.QDialog, Ui_ReportBedspace):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbProfileBed.setTable('rbHospitalBedProfile', True)
        self.lblInsurance.setVisible(False)
        self.cmbInsurance.setVisible(False)
        self.chkUngroupInsurer.setVisible(False)
        self.chkUngroupOrgStructure.setVisible(False)
        self.chkUngroupProfileBeds.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbInsurance.setValue(params.get('insurerId', None))
        self.cmbProfileBed.setValue(params.get('profileBed', None))
        self.chkUngroupInsurer.setChecked(params.get('ungroupInsurer', False))
        self.chkUngroupOrgStructure.setChecked(params.get('ungroupOrgStructure', False))
        self.chkUngroupProfileBeds.setChecked(params.get('ungroupProfileBed', False))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['insurerId'] = self.cmbInsurance.value()
        params['profileBed'] = self.cmbProfileBed.value()
        params['ungroupInsurer'] = self.chkUngroupInsurer.isChecked()
        params['ungroupOrgStructure'] = self.chkUngroupOrgStructure.isChecked()
        params['ungroupProfileBed'] = self.chkUngroupProfileBeds.isChecked()
        return params

    @QtCore.pyqtSlot(bool)
    def on_chkUngroupProfileBeds_clicked(self, checked):
        if not checked:
            self.chkUngroupOrgStructure.setChecked(False)


class CReceivedClients(QtGui.QDialog, Ui_ReportReceivedClients):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbProfileBed.setTable('rbHospitalBedProfile', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDateTime.setDateTime(params.get('edtBegDateTime', QtCore.QDateTime.currentDateTime()))
        self.edtEndDateTime.setDateTime(params.get('edtEndDateTime', QtCore.QDateTime.currentDateTime()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbProfileBed.setValue(params.get('profileBed', None))

    def params(self):
        params = {}
        params['edtBegDateTime'] = self.edtBegDateTime.dateTime()
        params['edtEndDateTime'] = self.edtEndDateTime.dateTime()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['profileBed'] = self.cmbProfileBed.value()

        return params

    @QtCore.pyqtSlot(bool)
    def on_chkUngroupProfileBeds_clicked(self, checked):
        if not checked:
            self.chkUngroupOrgStructure.setChecked(False)