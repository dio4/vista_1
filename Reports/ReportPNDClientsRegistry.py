# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceRef, forceString, getVal, formatName
from library.database import decorateString


def selectSocStatusData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId', None)
    socStatusClassId = params.get('socStatusClassId', None)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    sex = params.get('sex', 0)

    db = QtGui.qApp.db

    stmt = u'''
    SELECT Client.lastName, Client.firstName, Client.patrName, ClientSocStatus.endDate, rbAttachType.name as attachName, ClientAttach.orgStructure_id
    FROM Client
    LEFT JOIN rbAttachType ON rbAttachType.outcome = 0 AND rbAttachType.code = '1'
    LEFT JOIN ClientAttach ON rbAttachType.id = ClientAttach.attachType_id AND ClientAttach.client_id = Client.id AND Client.deleted = 0 AND ClientAttach.deleted = 0 AND (ClientAttach.endDate IS NULL OR ClientAttach.endDate > %s)
    INNER JOIN ClientSocStatus ON ClientSocStatus.client_id = Client.id AND ClientSocStatus.deleted = 0
    WHERE %s
    ORDER BY ClientAttach.orgStructure_id, rbAttachType.name, Client.lastName, Client.firstName, Client.patrName
    '''

    tableClientSocStatus = db.table('ClientSocStatus')
    tableClientAttach = db.table('ClientAttach')
    # tableAttachType = db.table('rbAttachType')
    tableClient = db.table('Client')
    cond = []
    cond.append(tableClientSocStatus['endDate'].between(begDate, endDate))
    cond.append(tableClientSocStatus['socStatusClass_id'].eq(socStatusClassId))
    if ageFrom <= ageTo:
        cond.append('age(Client.birthDate, CURRENT_DATE) BETWEEN %s AND %s' % (ageFrom, ageTo))

    if sex:
        cond.append(tableClient['sex'].eq(sex))

    orgStructureIdList = []
    if orgStructureId:
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))

    return db.query(stmt % (endDate.toString(QtCore.Qt.ISODate), db.joinAnd(cond))), orgStructureIdList


def selectEventData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId', None)
    eventTypeId = params.get('eventTypeId', None)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    sex = params.get('sex', 0)

    db = QtGui.qApp.db

    stmt = u'''
    SELECT Client.lastName, Client.firstName, Client.patrName, Event.execDate as endDate, rbAttachType.name AS attachName
    FROM Client
    INNER JOIN ClientAttach ON ClientAttach.client_id = Client.id AND Client.deleted = 0 AND ClientAttach.deleted = 0 AND (ClientAttach.endDate IS NULL OR ClientAttach.endDate > %(endDate)s)
    INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id AND rbAttachType.code IN ('4', '5')
    LEFT JOIN rbAttachType AS at ON at.code = '1'
    LEFT JOIN ClientAttach AS ca ON at.id = ca.attachType_id AND ca.client_id = Client.id AND ca.deleted = 0 AND (ca.endDate IS NULL OR ca.endDate > %(endDate)s)

    INNER JOIN Event ON Event.client_id = Client.id AND Event.deleted = 0
    WHERE %(cond)s
    ORDER BY rbAttachType.name, Client.lastName, Client.firstName, Client.patrName
    '''

    tableEvent = db.table('Event')
    tableClientAttach = db.table('ClientAttach').alias('ca')
    tableClient = db.table('Client')
    cond = []
    cond.append(tableEvent['execDate'].between(begDate, endDate))
    cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if ageFrom <= ageTo:
        cond.append('age(Client.birthDate, CURRENT_DATE) BETWEEN %s AND %s' % (ageFrom, ageTo))

    if sex:
        cond.append(tableClient['sex'].eq(sex))

    if orgStructureId:
        cond.append(tableClientAttach['orgStructure_id'].eq(orgStructureId))

    return db.query(stmt % {'endDate': decorateString(endDate.toString(QtCore.Qt.ISODate)),
                            'cond': db.joinAnd(cond)})


def selectDisabilityData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId', None)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    sex = params.get('sex', 0)

    db = QtGui.qApp.db

    stmt = u'''
    SELECT Client.lastName, Client.firstName, Client.patrName, ClientDisability.recertificationDate as endDate, rbAttachType.name as attachName, ClientAttach.orgStructure_id
    FROM Client
    LEFT JOIN rbAttachType ON rbAttachType.outcome = 0
    LEFT JOIN ClientAttach ON rbAttachType.id = ClientAttach.attachType_id AND ClientAttach.client_id = Client.id AND Client.deleted = 0 AND ClientAttach.deleted = 0 AND (ClientAttach.endDate IS NULL OR ClientAttach.endDate > %s)
    INNER JOIN ClientDisability ON ClientDisability.client_id = Client.id
    WHERE %s
    AND (DATE(ClientAttach.endDate) is NULL OR DATE(ClientAttach.endDate) = "")
    ORDER BY ClientAttach.orgStructure_id, rbAttachType.name, Client.lastName, Client.firstName, Client.patrName
    '''

    tableClientAttach = db.table('ClientAttach')
    tableClient = db.table('Client')
    tableClientDisability = db.table('ClientDisability')
    cond = [
        tableClientDisability['recertificationDate'].between(begDate, endDate)
    ]

    if ageFrom <= ageTo:
        cond.append('age(Client.birthDate, CURRENT_DATE) BETWEEN %s AND %s' % (ageFrom, ageTo))

    if sex:
        cond.append(tableClient['sex'].eq(sex))

    if orgStructureId:
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))

    return db.query(stmt % (endDate.toString(QtCore.Qt.ISODate), db.joinAnd(cond)))


class CReportPNDClientsRegistry(CReport):
    def __init__(self, parent, mode=0):
        """
        mode = 0 - по социальным статусам, 1 - по типам обращений, 2 - по инвалидностям.
        """
        CReport.__init__(self, parent)
        if mode == 0:
            self.setTitle(u'Список пациентов, срок действия социальных статусов которых истекает.')
        elif mode in (1, 2):
            self.setTitle(u'Список пациентов, которым необходимо пройти переосвидетельствование.')
        self.mode = mode

    def getSetupDialog(self, parent):
        result = CReportPNDClientsRegistrySetupDialog(parent)
        result.setTitle(self.title())
        if self.mode == 0:
            result.setSocStatusVisible(True)
        elif self.mode == 1:
            result.setEventTypeVisible(True)
        return result

    def build(self, params):
        lastAttachType = None
        # Prepare report template
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        if self.mode == 2:
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Переосвидетельствование (по инвалидности)')
            cursor.insertBlock()

        self.dumpParams(cursor, params)

        if self.mode == 2:
            tableColumns = [
                ('5%', [u'№'], CReportBase.AlignLeft),
                ('65%', [u'Ф.И.О.'], CReportBase.AlignLeft),
                ('10%', [u'Территориал'], CReportBase.AlignLeft),
                ('30%', [u'Дата окончания'], CReportBase.AlignRight)
            ]
            table = createTable(cursor, tableColumns)
            orgStructureIdList = []
            if self.mode == 0:
                query, orgStructureIdList = selectSocStatusData(params)
            elif self.mode == 1:
                query = selectEventData(params)
            elif self.mode == 2:
                query = selectDisabilityData(params)
            lastOrgStructureId = None
            number = 1
            while query.next():
                record = query.record()
                attachType = forceString(record.value('attachName'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                if len(orgStructureIdList) > 1:
                    if orgStructureId and orgStructureId != lastOrgStructureId:
                        i = table.addRow()
                        table.mergeCells(i, 0, 1, 4)
                        orgStructureName = forceString(
                            QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
                        table.setText(i, 1, orgStructureName, CReportBase.TableTotal)
                        lastOrgStructureId = orgStructureId
                        lastAttachType = None
                if attachType and attachType != lastAttachType:
                    i = table.addRow()
                    number = 1
                    table.mergeCells(i, 0, 1, 4)
                    table.setText(i, 0, attachType, fontBold=True)
                    lastAttachType = attachType
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                name = formatName(lastName, firstName, patrName)
                date = forceString(record.value('endDate'))
                i = table.addRow()
                table.setText(i, 0, number)
                table.setText(i, 1, name)
                # номер участка к которому прикреплен пациент
                if orgStructureId:
                    table.setText(
                        i, 2, forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
                    )
                else:
                    table.setText(i, 2, u' - ')

                table.setText(i, 3, date)
                number += 1
        else:
            tableColumns = [
                ('70%', [u'Ф.И.О.'], CReportBase.AlignLeft),
                ('35%', [u'Дата окончания'], CReportBase.AlignRight)
            ]
            table = createTable(cursor, tableColumns)
            orgStructureIdList = []
            if self.mode == 0:
                query, orgStructureIdList = selectSocStatusData(params)
            elif self.mode == 1:
                query = selectEventData(params)
            elif self.mode == 2:
                query = selectDisabilityData(params)
            lastOrgStructureId = None
            while query.next():
                record = query.record()
                attachType = forceString(record.value('attachName'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                if len(orgStructureIdList) > 1:
                    if orgStructureId and orgStructureId != lastOrgStructureId:
                        i = table.addRow()
                        table.mergeCells(i, 0, 1, 2)
                        orgStructureName = forceString(
                            QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
                        table.setText(i, 0, orgStructureName, CReportBase.TableTotal)
                        lastOrgStructureId = orgStructureId
                        lastAttachType = None
                if attachType and attachType != lastAttachType:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 2)
                    table.setText(i, 0, attachType, fontBold=True)
                    lastAttachType = attachType
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                name = formatName(lastName, firstName, patrName)
                date = forceString(record.value('endDate'))
                i = table.addRow()
                table.setText(i, 0, name)
                table.setText(i, 1, date)
        return doc


from Ui_ReportPNDClientsRegistrySetup import Ui_ReportPNDClientsRegistrySetupDialog


class CReportPNDClientsRegistrySetupDialog(QtGui.QDialog, Ui_ReportPNDClientsRegistrySetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.isSocStatusVisible = False
        self.isEventTypeVisible = False

        self.setSocStatusVisible(self.isSocStatusVisible)
        self.setEventTypeVisible(self.isEventTypeVisible)
        self.cmbEventType.setTable('EventType')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setSocStatusVisible(self, flag):
        self.cmbSocStatusClass.setVisible(flag)
        self.lblSocStatusClass.setVisible(flag)
        self.isSocStatusVisible = flag

    def setEventTypeVisible(self, flag):
        self.cmbEventType.setVisible(flag)
        self.lblEventType.setVisible(flag)
        self.isEventTypeVisible = flag

    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate().currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate().currentDate()))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

    def params(self):
        result = {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'sex': self.cmbSex.currentIndex(),
            'ageFrom': self.edtAgeFrom.value(),
            'ageTo': self.edtAgeTo.value(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'eventTypeId': self.cmbEventType.value(),
            'socStatusClassId': self.cmbSocStatusClass.value()
        }

        return result


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pnd6',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportPNDClientsRegistry(None)
    w.mode = 2
    w.exec_()


if __name__ == '__main__':
    main()
