# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Ui_ReportCancellationReason import Ui_Dialog
from library.LoggingModule.Logger import getLoggerDbName
from library.Utils import getVal, forceString, forceDate


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    personId = params.get('personId', None)
    orgStructureId = params.get('orgStructureId', None)

    stmt = u"""
SELECT
    Event.id AS eventId,
    Client.id AS clientId,
    CONCAT_WS(" ", Client.lastName, Client.firstName, Client.patrName) AS clientName,
    ehp.dateFrom AS  dateFrom,
    ehp.dateTo AS  dateTo,
    Person.name AS personName,
    ehp.comment AS  comment
FROM
    {logger}.EventHospTransfer ehp
    INNER JOIN Event ON Event.id = ehp.event_id
    INNER JOIN Client ON Event.client_id = Client.id
    INNER JOIN vrbPersonWithSpeciality Person ON Person.id = ehp.person_id
    INNER JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
WHERE
    ehp.deleted = 0
    AND Event.deleted = 0
    AND Client.deleted = 0
    AND {cond}
ORDER BY
    clientName
"""

    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    tblEvent = db.table('Event')

    cond = []
    cond.append(tblEvent['execDate'].dateBetween(begDate, endDate))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if personId:
        cond.append(tablePerson['id'].eq(personId))

    return db.query(stmt.format(logger=getLoggerDbName(), cond=db.joinAnd(cond)))


class CReportHospitalizationTransferReason(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Отчет по причинам переносов госпитализаций')

    def getSetupDialog(self, parent):
        result = CReportHospitalizationTransferReasonDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('10?', [u'Код карточки'], CReportBase.AlignLeft),
            ('10?', [u'Код пациента'], CReportBase.AlignLeft),
            ('20?', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('10?', [u'Прошлая дата госпитализации'], CReportBase.AlignLeft),
            ('10?', [u'Текущая дата госпитализации'], CReportBase.AlignLeft),
            ('20?', [u'ФИО врача'], CReportBase.AlignLeft),
            ('20?', [u'Причина переноса'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                forceString(record.value('eventId')),
                forceString(record.value('clientId')),
                forceString(record.value('clientName')),
                forceDate(record.value('dateFrom')).toString('dd.MM.yyyy'),
                forceDate(record.value('dateTo')).toString('dd.MM.yyyy'),
                forceString(record.value('personName')),
                forceString(record.value('comment')),
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val)
        return doc


class CReportHospitalizationTransferReasonDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lblPeriod.setText(u"Дата окончания обращения:")
        self.cmbOrgStruct.setValue(QtGui.qApp.currentOrgStructureId)
        self.dtFrom.setDate(QtCore.QDate.currentDate())
        self.dtTo.setDate(QtCore.QDate.currentDate())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.dtFrom.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.dtTo.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbOrgStruct.setValue(getVal(params, 'orgStructureId', None))

    def params(self):
        result = {}
        result['begDate'] = self.dtFrom.date()
        result['endDate'] = self.dtTo.date()
        result['personId'] = self.cmbPerson.value()
        result['orgStructureId'] = self.cmbOrgStruct.value()
        return result


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pes',
        'port': 3306,
        'database': 's12',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportHospitalizationTransferReason(None)
    w.exec_()


if __name__ == '__main__':
    main()
