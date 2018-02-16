# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectLeaved(params):
    stmt = u'''
    SELECT Event.id AS eventId,
        OrgStructure.name AS orgName
        FROM Event
        INNER JOIN EventType ON Event.eventType_id = EventType.id and EventType.deleted = 0
        INNER JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
        INNER JOIN Client ON Event.client_id = Client.id and Client.deleted = 0

        INNER JOIN Action ON Event.id = Action.event_id and Action.deleted = 0
        INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.deleted = 0 AND ActionType.name like 'выписка'
        INNER JOIN ActionPropertyType ON ActionType.id = ActionPropertyType.actionType_id AND ActionPropertyType.name = 'отделение' and ActionPropertyType.deleted = 0
        INNER JOIN ActionProperty ON ActionPropertyType.id = ActionProperty.type_id AND Action.id = ActionProperty.action_id AND ActionProperty.deleted = 0
        INNER JOIN ActionProperty_OrgStructure ON ActionProperty.id = ActionProperty_OrgStructure.id
        INNER JOIN OrgStructure ON ActionProperty_OrgStructure.value = OrgStructure.id AND OrgStructure.deleted = 0

        WHERE (DATE(Event.setDate) >= DATE('%s') AND DATE(Event.setDate) <= DATE('%s')  OR
        (DATE(Event.execDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s')))
        AND rbEventProfile.regionalCode IN (11, 12, 301, 302, 401, 402)
        #GROUP BY client.id HAVING COUNT(client.id) >= 2
        ORDER BY Client.id
    ;
      '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

def selectData(params):
    stmt = u'''
        SELECT GetClients.ClientId AS clientId, CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS FIO,
          DATE(Event.setDate) AS eventSetDate, DATE(Event.execDate) AS eventExecDate, Event.id AS eventId,
          Client.birthDate AS birthDate,
          Diagnosis.MKB AS MKB,
          CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS FIO_Doctors
         FROM (

          SELECT Client.id AS ClientId
          FROM Event
          INNER JOIN EventType ON Event.eventType_id = EventType.id and EventType.deleted = 0
          INNER JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
          INNER JOIN Client ON Event.client_id = Client.id and Client.deleted = 0

          WHERE (DATE(Event.setDate) >= DATE('%s') AND DATE(Event.setDate) <= DATE('%s')  OR
                (DATE(Event.execDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s')))

          AND rbEventProfile.regionalCode IN  (11, 12, 301, 302, 401, 402)
          GROUP BY Client.id
          HAVING COUNT(Client.id) >= 2
          ORDER BY Client.id
        ) GetClients

        INNER JOIN Client ON GetClients.ClientId = Client.id AND Client.deleted = 0
        INNER JOIN Event ON Client.id = Event.client_id AND Event.deleted = 0
        INNER JOIN EventType ON Event.eventType_id = EventType.id and EventType.deleted = 0
        INNER JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
        INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id AND Diagnostic.deleted = 0
        INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0
        INNER JOIN Action ON Event.id = Action.event_id
        INNER JOIN Person On Action.person_id = Person.id

        WHERE (DATE(Event.setDate) >= DATE('%s') AND DATE(Event.setDate) <= DATE('%s')  OR
                (DATE(Event.execDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s')))
           AND rbEventProfile.regionalCode IN  (11, 12, 301, 302, 401, 402)
        GROUP BY Event.id
        ORDER BY Client.id, Event.setDate
;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

class CReportReHospitalizationSetupDialog(QtGui.QDialog, Ui_ReportReHospitalizationSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportReHospitalization(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Отчёт анализирующий повторные госпитализации пациентов в течение 30 дней по одному и тому же заболеванию")

    def getSetupDialog(self, parent):
        result = CReportReHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('26%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('8%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('15%', [u'Период госпитализации'], CReportBase.AlignLeft),
            ('5%', [u'Диагноз'], CReportBase.AlignLeft),
            ('20%', [u'Oтделение выписки'], CReportBase.AlignLeft),
            ('26%', [u'ФИО врача'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        #
        # if you don't call queryNext again, with selectData(params), instead of
        # assigning queryNext = query, there will be just one pointer for both variables, pointing to record.next()
        #
        queryNext = selectData(params)
        queryNext.next()

        queryLeaved = selectLeaved(params)
        dictLeaved = {}
        while queryLeaved.next():
            record = queryLeaved.record()
            dictLeaved[forceString(record.value("eventId"))] = forceString(record.value("orgName"))

        while query.next():
            queryNext.next()
            record = query.record()
            recordNext = queryNext.record()

            if forceString(record.value('clientId')) == forceString(recordNext.value('clientId'))\
                and forceString(record.value('MKB')) == forceString(recordNext.value('MKB')) \
                and forceDate(record.value('eventExecDate')).daysTo(forceDate(recordNext.value('eventSetDate'))) <= 30\
                and forceString(record.value('eventId')) in dictLeaved.keys():
                i = table.addRow()
                dateRangeRecord = " - ".join([forceString(record.value('eventSetDate')), forceString(record.value('eventExecDate'))])
                dateRangeRecordNext = " - ".join([forceString(recordNext.value('eventSetDate')), forceString(recordNext.value('eventExecDate'))])
                table.setText(i, 0, forceString(record.value('FIO')))
                table.setText(i, 1, forceString(record.value('birthdate')))
                table.setText(i, 2, forceString(dateRangeRecord))
                table.setText(i, 3, forceString(record.value('MKB')))
                table.setText(i, 4, forceString(dictLeaved[forceString(record.value('eventId'))]))
                table.setText(i, 5, forceString(record.value('FIO_Doctors')))
                i = table.addRow()

                table.setText(i, 0, forceString(recordNext.value('FIO')))
                table.setText(i, 1, forceString(recordNext.value('birthdate')))
                table.setText(i, 2, forceString(dateRangeRecordNext))
                table.setText(i, 3, forceString(recordNext.value('MKB')))
                if forceString(recordNext.value('eventId')) in dictLeaved.keys():
                    table.setText(i, 4, forceString(dictLeaved[forceString(recordNext.value('eventId'))]))
                table.setText(i, 5, forceString(recordNext.value('FIO_Doctors')))

        return doc

def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.207',
                      'port' : 3306,
                      'database' : 'belaya_glina',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    """
    connectionInfo = {'driverName' : 'mysql',
                  'host' : '192.168.0.207',
                  'port' : 3306,
                  'database' : 'olyu_sochi2',
                  'user' : 'dbuser',
                  'password' : 'dbpassword',
                  'connectionName' : 'vista-med',
                  'compressData' : True,
                  'afterConnectFunc' : None}
    """
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportReHospitalization(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()