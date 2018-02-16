# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Registry.Utils import formatAddress, getAddress, getClientAddress, getClientInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceInt, forceString, toVariant, getVal, getInfisCodes
from library.database import addDateInRange

groupTitles = []
reg_num=0
reg_ind={}

def selectData(begDate, endDate,  eventTypeId, PermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
SELECT distinct
    lpu_OKATO.NAME as lpu_region, Event.client_id as clientId,
    lpu.infisCode, ClientAttach.LPU_id
FROM
    Event
    JOIN Client            ON Client.id = Event.client_id
    LEFT JOIN ClientAttach ON ClientAttach.id=(
        select max(ca.id)
        from ClientAttach as ca join rbAttachType on ca.attachType_id=rbAttachType.id
        where ca.client_id=Event.client_id and rbAttachType.temporary=0 and rbAttachType.outcome=0)
    LEFT JOIN Organisation as lpu on lpu.id = ClientAttach.LPU_id
    LEFT JOIN kladr.OKATO as lpu_OKATO on lpu_OKATO.CODE=left(lpu.OKATO, 5)
    LEFT JOIN Account_Item ON (
        Account_Item.event_id = Event.id AND
        Account_Item.deleted = 0 AND
        Account_Item.id = (
            SELECT max(AI.id)
            FROM Account_Item AS AI
            WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL))
WHERE
    Event.deleted = 0 AND %s
ORDER BY
    Client.lastName, Client.firstName, Client.patrName
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    setDate  = tableEvent['setDate']
    execDate = tableEvent['execDate']
    cond = []
    dateCond = []
    dateCond.append(db.joinAnd([setDate.le(endDate), execDate.isNull()]))
    dateCond.append(db.joinAnd([execDate.ge(begDate), execDate.le(endDate)]))
    dateCond.append(db.joinAnd([setDate.ge(begDate), execDate.le(endDate)]))
    cond.append(db.joinOr(dateCond))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if PermanentAttach and PermanentAttach>0:
        cond.append('ClientAttach.LPU_id=%d' % PermanentAttach)
    elif PermanentAttach==-1:
        cond.append('ClientAttach.id is null')
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    my_org_id=forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'orgId', None))
    cond.append(tableEvent['org_id'].eq(my_org_id))
    stmt=stmt % db.joinAnd(cond)
    return db.query(stmt)


class CStatReportF131Raion(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Сводка по Ф.131 по району', u'Сводка по Ф.131')

    def getSetupDialog(self, parent):
        result = CStatReportF131RaionSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        global groupTitles
        global reg_num
        global reg_ind
        groupTitles = []
        reg_num=0
        reg_ind={}

        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)
        PermanentAttach = getVal(params, 'PermanentAttach', None)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())
        Raion = forceString(getVal(params, 'Raion', None))
        YearDD = forceString(getVal(params, 'YearForDD', ''))
        reportRowSize = 4
        reportDataByGroups = []
        reportData = []
        query = selectData(begDate, endDate, eventTypeId, PermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        num=0
        while query.next() :
            record = query.record()
            region=''
            lpu_infis=forceString(record.value('infisCode'))
            if record.value('LPU_id'):
                if lpu_infis.strip():
                    region = forceString(record.value('lpu_region')).strip()
                else:
                    lpu_infis=u'нет прикрепления'
            else:
                lpu_infis=u'нет прикрепления'
            clientId=forceInt(record.value('clientId'))
            clientInfo=getClientInfo(clientId)
            fio=clientInfo['lastName']+' '+clientInfo['firstName']+' '+clientInfo['patrName']
            if not region:
                region, KLADRCode = getRegion(clientId)
                if Raion==u'Иногородние' and KLADRCode[:2] in ['78', '47']:
                    continue
            else:
                if Raion==u'Иногородние':
                    continue
            if Raion==u'Неидентифицированные':
                if region:
                    continue
            else:
                if region!=Raion and Raion!=u'Иногородние':
                    continue
            bd=forceString(clientInfo['birthDate'])
            adr=get_adr(clientId)
            ind=reg_ind.get(region, -1)
            if ind==-1:
                groupTitles.append(region)
                reg_ind[region]=reg_num
                ind=reg_num
                reg_num+=1
                reportDataByGroups.append([])
            reportData = reportDataByGroups[ind]
            reportData.append([lpu_infis, fio, bd, adr])
            num+=1

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportBody)
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportTitle)
        org_reg=forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'region'))
        if not org_reg:
            OKATO=forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OKATO'))
            org_reg=forceString(QtGui.qApp.db.translate('kladr.OKATO', 'CODE', OKATO[:5], 'NAME'))
        cursor.insertText(
u'''Акт передачи форм № 131.у-%s
%s район Санкт-Петербурга
''' % (YearDD, org_reg))
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        lpu=forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'shortName'))
        OGRN=forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))

        if Raion!=u'Иногородние' and Raion!=u'Ленинградская обл.' and Raion!=u'Неидентифицированные' and Raion!=u'Административные районы г Санкт-Петербург':
            dest = Raion+u' район Санкт-Петербурга'
        else:
            dest = Raion
        prik=u''
        if PermanentAttach and PermanentAttach>0:
            lpu2=forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', PermanentAttach, 'shortName'))
#            dest=u'учреждение здравоохранения '+lpu2
            prik=u' '+lpu2
        cursor.insertText(
u'''%s (ОГРН %s)
передаёт в %s
формы № 131.у-%s "Карта учёта дополнительной диспансеризации гражданина" с результатами лабораторных и функциональных исследований в количестве %d по месту прикрепления к лечебно-профилактическому учреждению%s на следующих граждан:
''' % (lpu, OGRN, dest, YearDD, num, prik))
        cursor.insertBlock()

        tableColumns = [
              ('10%', [ u'№' ], CReportBase.AlignLeft),
              ('30%', [ u'ФИО' ], CReportBase.AlignLeft),
              ('10%', [ u'Дата рождения' ], CReportBase.AlignLeft),
              ('50%', [ u'Адрес' ], CReportBase.AlignLeft),
                       ]

        table = createTable(cursor, tableColumns)

        rd=[]
        for i in range(len(groupTitles)):
            rd.append((groupTitles[i], reportDataByGroups[i]))
        rd.sort(key=(lambda x:x[0]))
        if rd and not rd[0][0]:
            rd=rd[1:]+[rd[0]]

        totalByReport = 0
        for Title, reportData in rd:
            if reportData:
                totalByGroup = len(reportData)
                totalByReport += totalByGroup
                for i, reportLine in enumerate(reportData):
                    i = table.addRow()
                    table.setText(i, 0, i)
                    for j in xrange(1, reportRowSize):
                        table.setText(i, j, reportLine[j])
        self.addTotal(table, u'Всего', totalByReport)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)

        cursor.insertBlock()
        org_chief=forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'chief'))
        cursor.insertText(
u'''
Главный врач %s %s района ________________ / %s /

Формы № 131/у-%s "Карта учёта дополнительной диспансеризации гражданина" с результатами лабораторных и функциональных исследований в количестве %d:

''' % (lpu, name_pad(org_reg), org_chief, YearDD, num))
        cursor.insertBlock()

        rows = []
        rows.append([u'Начальник отдела здравоохранения', u'Начальник отдела здравоохранения'])
        rows.append([u'%s района Санкт-Петербурга' % name_pad(org_reg), u'%s района Санкт-Петербурга' % name_pad(Raion)])
        rows.append([u'\n\n', u'\n\n'])
        rows.append([u'Передал ________________________________', u'Принял ________________________________'])
        rows.append([u'        (подпись, расшифровка подписи)',  u'        (подпись, расшифровка подписи)'])
        rows.append([u'\n', u'\n'])
        columnDescrs = [('50%', [], CReportBase.AlignCenter), ('50%', [], CReportBase.AlignCenter)]
        table1 = createTable (
            cursor, columnDescrs, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            table1.setText(i, 0, row[0])
            table1.setText(i, 1, row[1])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        return doc

    def addTotal(self, table, title, reportLen):
        i = table.addRow()
        table.mergeCells(i, 1, 1, 3)
        table.setText(i, 0, title, CReportBase.TableTotal)
        table.setText(i, 1, reportLen)

def getRegion(clientId):
    region = ''
    KLADRCode = ''
    clientAddressRecord = getClientAddress(clientId, 0)
    if clientAddressRecord:
        address = getAddress(clientAddressRecord.value('address_id'))
        KLADRCode = address.KLADRCode
        area, region, npunkt, street, streettype = getInfisCodes(
            KLADRCode, address.KLADRStreetCode,
            address.number, address.corpus)
        region = forceString(QtGui.qApp.db.translate('kladr.OKATO', 'infis', area, 'NAME'))
        if area == u'ЛО':
            region = u'Ленинградская обл.'
    return region, KLADRCode

def get_adr(clientId):
    regAddressRecord = getClientAddress(clientId, 0)
    if regAddressRecord:
        return formatAddress(regAddressRecord.value('address_id'))
    return ''

from Ui_StatReportF131RaionSetup import Ui_StatReportF131RaionSetupDialog

class CStatReportF131RaionSetupDialog(QtGui.QDialog, Ui_StatReportF131RaionSetupDialog):
    def __init__(self, parent=None):
        db = QtGui.qApp.db
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)
        self.edtBegPayDate.setDate(QtCore.QDate())
        self.edtEndPayDate.setDate(QtCore.QDate())

        self.cmbPermanentAttach.addItem(u'не задано', toVariant(None))
        self.cmbPermanentAttach.addItem(u'без прикрепления', toVariant(-1))
        query = db.query('SELECT id, shortName FROM Organisation WHERE exists (select * from ClientAttach where ClientAttach.LPU_id=Organisation.id) order by shortName')
        while query.next() :
            record = query.record()
            id   = record.value(0).toInt()[0]
            shortName = forceString(record.value(1))
            self.cmbPermanentAttach.addItem(shortName, toVariant(id))

        self.cmbRaion.addItem(u'Иногородние', toVariant(u'Иногородние'))
        self.cmbRaion.addItem(u'Неидентифицированные', toVariant(u'Неидентифицированные'))
        self.cmbRaion.addItem(u'Ленинградская обл.', toVariant(u'Ленинградская обл.'))
        query = db.query('SELECT NAME FROM kladr.OKATO WHERE P1<>"   " and P2="   "') # районы Петербурга и Лен. области
        while query.next() :
            record = query.record()
            NAME = record.value(0).toString()
            self.cmbRaion.addItem(NAME, toVariant(NAME))

        YearDD = u''
        curDate = QtCore.QDate.currentDate()
        curYear = curDate.toString('yy')
        YearDD = u'ДД-' + curYear
        self.ledtYearForDD.setText(YearDD)


    def setPayPeriodVisible(self, value):
        pass

    def setWorkTypeVisible(self, value):
        pass

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setEventTypeVisible(self, visible=True):
        pass

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.chkOnlyPayedEvents.setChecked(params.get('onlyPayedEvents', False))
        self.edtBegPayDate.setDate(params.get('begPayDate', QtCore.QDate.currentDate()))
        self.edtEndPayDate.setDate(params.get('endPayDate', QtCore.QDate.currentDate()))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()

        PermanentAttach=self.cmbPermanentAttach.currentText()
        if PermanentAttach==u'не задано':
            PermanentAttach=None
        elif PermanentAttach==u'без прикрепления':
            PermanentAttach=-1
        else:
            PermanentAttach=forceInt(QtGui.qApp.db.translate(
            'Organisation', 'shortName', PermanentAttach, 'id'))
        result['PermanentAttach'] = PermanentAttach

        Raion=self.cmbRaion.currentText()
        result['Raion'] = Raion

        result['onlyPayedEvents'] = self.chkOnlyPayedEvents.isChecked()
        result['begPayDate'] = self.edtBegPayDate.date()
        result['endPayDate'] =self.edtEndPayDate.date()
        result['YearForDD'] =self.ledtYearForDD.text()
        return result

def name_pad(name):
    if name==u'Петро-Славянка':
        return name
    if name==u'Красное Село':
        return u'Красносельского'
    if name==u'Кронштадт':
        return u'Кронштадтского'
    if name==u'Стрельна':
        return u'Стрельнинского'
    if name[-2:] in [u'ий', u'ый']:
        return name[:-2]+u'ого'
    if name[-1:] in [u'о',  u'а']:
        return name[:-1]+u'ского'
    if name[-1:] == u'к':
        return name+u'ого'
    if name[-2:] in [u'ов', u'оф']:
        return name+u'ского'


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pz12',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CStatReportF131Raion(None)
    w.exec_()


if __name__ == '__main__':
    main()
