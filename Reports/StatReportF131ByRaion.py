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
from Reports.ReportSetupDialog import CReportSetupDialog
from Reports.StatReport1NPUtil import havePermanentAttach
from library.Utils import forceInt, forceString, getVal, getInfisCodes
from library.database import addDateInRange

groupTitles = []
reg_num=0
reg_ind={}

def selectData(begDate, endDate,  eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, primaryMarkIndex):
    stmt="""
        SELECT distinct
            lpu_OKATO.NAME as lpu_region, Event.client_id as clientId,
            lpu.infisCode, ClientAttach.LPU_id
        FROM Event
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
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    my_org_id=forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'orgId', None))
    cond.append(tableEvent['org_id'].eq(my_org_id))
    if primaryMarkIndex != 0:
        cond.append(tableEvent['isPrimary'].eq(primaryMarkIndex))
    stmt=stmt % db.joinAnd(cond)
    return db.query(stmt)


class CStatReportF131ByRaion(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Сводка по Ф.131 по районам', u'Сводка по Ф.131')

    def getSetupDialog(self, parent):
        result = CStatReportF131ByRaionSetup(parent)
        result.setPayPeriodVisible(self.payPeriodVisible)
        result.setWorkTypeVisible(self.workTypeVisible)
        result.setOwnershipVisible(self.ownershipVisible)
        result.setTitle(self.title())


        result.lblIsPrimary = QtGui.QLabel(result)
        result.lblIsPrimary.setText(u'Признак первичности')
        result.gridLayout.addWidget(result.lblIsPrimary, 11, 0, 1, 1)
        result.cmbPrimaryMark = QtGui.QComboBox(result)
        result.gridLayout.addWidget(result.cmbPrimaryMark, 11, 1, 1, 9)
        result.cmbPrimaryMark.addItems([u'Все обращения', u'Первичные обращения', u'Вторичные обращения'])

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
        onlyPermanentAttach = getVal(params, 'onlyPermanentAttach', False)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())

        primaryMarkIndex = params.get('primaryMarkIndex', 0)

        reportRowSize = 4
        reportDataByGroups = []
        reportData = []
        query = selectData(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, primaryMarkIndex)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next() :
            record = query.record()
            region=''
            lpu_infis=forceString(record.value('infisCode'))
            if record.value('LPU_id'):
                if lpu_infis.strip():
                    region = forceString(record.value('lpu_region')).strip()
                else:
                    lpu_infis=u'нет прикрепления'
            else: lpu_infis=u'нет прикрепления'
            clientId=forceInt(record.value('clientId'))
            clientInfo=getClientInfo(clientId)
            fio=clientInfo['lastName']+' '+clientInfo['firstName']+' '+clientInfo['patrName']
            if not region:
#                region = forceString(record.value('reg_region')).strip()
                region = getRegion(clientId)
            bd=forceString(clientInfo['birthDate'])
#            adr=''
#            adr=formatAddress(record.value('address_id'))
            adr=get_adr(clientId)
#            adr=clientInfo.get('regAddress', '')
            ind=reg_ind.get(region, -1)
            if ind==-1:
                groupTitles.append(region)
                reg_ind[region]=reg_num
                ind=reg_num
                reg_num+=1
                reportDataByGroups.append([])
            reportData = reportDataByGroups[ind]
            reportData.append([lpu_infis, fio, bd, adr])

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сводка по Ф.131 по районам')
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
              ('10%', [ u'Код ЛПУ' ], CReportBase.AlignLeft ),
              ('30%', [ u'ФИО' ], CReportBase.AlignLeft ),
              ('10%', [ u'Дата рождения' ], CReportBase.AlignLeft ),
              ('50%', [ u'Адрес' ], CReportBase.AlignLeft ),
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
                self.addGroupHeader(table, Title)
                for i, reportLine in enumerate(reportData):
                    i = table.addRow()
                    for j in xrange(reportRowSize):
                        table.setText(i, j, reportLine[j])
                self.addTotal(table, u'всего по району', totalByGroup)
        self.addTotal(table, u'Всего', totalByReport)
        return doc


    def addGroupHeader(self, table, group):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 4)
        if not group: group=u'прочие районы'
        table.setText(i, 0, group, CReportBase.TableHeader)


    def addTotal(self, table, title, reportLen):
        i = table.addRow()
        table.mergeCells(i, 1, 1, 3)
        table.setText(i, 0, title, CReportBase.TableTotal)
        table.setText(i, 1, reportLen)


class CStatReportF131ByRaionSetup(CReportSetupDialog):

    def __init__(self, parent=None):
        CReportSetupDialog.__init__(self, parent)

    def params(self):
        result = CReportSetupDialog.params(self)
        result['primaryMarkIndex'] = self.cmbPrimaryMark.currentIndex()
        return result

    def setParams(self, params):
        CReportSetupDialog.setParams(self, params)
        self.cmbPrimaryMark.setCurrentIndex(params.get('primaryMarkIndex', 0))


def getRegion(clientId):
#    if clientId == 2930:
#        pass
    clientAddressRecord = getClientAddress(clientId, 0)
    if clientAddressRecord:
        address = getAddress(clientAddressRecord.value('address_id'))
#        if not addressInfo:
#            pass
        area, region, npunkt, street, streettype = getInfisCodes(
            address.KLADRCode, address.KLADRStreetCode,
            address.number, address.corpus)
#        if not area:
#            pass
        region = forceString(QtGui.qApp.db.translate('kladr.OKATO', 'infis', area, 'NAME'))
        if area == u'ЛО':
            region = u'Ленинградская обл.'
#        if not region:
#            pass
        return region
    else:
        return ''


def get_adr(clientId):
    regAddressRecord = getClientAddress(clientId, 0)
    if regAddressRecord:
        return formatAddress(regAddressRecord.value('address_id'))
    return ''
#    freeInput, KLADRCode, KLADRStreetCode, house, corpus, flat = getClientAddressEx(clientId)
#    return freeInput


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

    w = CStatReportF131ByRaion(None)
    w.exec_()


if __name__ == '__main__':
    main()
