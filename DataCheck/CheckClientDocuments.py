# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from CCheck import CCheck
from DataCheck.Ui_ClientDocuments import Ui_ClientDocumentsCheckDialog
from Registry.ClientEditDialog import CClientEditDialog
from Registry.Utils import getClientDocument
from Users.Rights import urAdmin, urRegTabWriteRegistry
from library.Utils import forceInt, forceString, forceDate, forceRef


class CClientDocumentsCheck(QtGui.QDialog, Ui_ClientDocumentsCheckDialog, CCheck):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CCheck.__init__(self)

        currentDate = QtCore.QDate.currentDate()
        self.begDate.setDate(QtCore.QDate(currentDate.year(), 1, 1))
        self.endDate.setDate(currentDate)

    def check(self):
        def val(name):
            return record.value(name)

        db = QtGui.qApp.db
        query = u"""
        SELECT DISTINCTROW
            Client.id AS client_id,
            CONCAT_WS(' ' , Client.lastName, Client.firstName, Client.patrName) AS fullName # ,
            # ClientDocument.id AS docId,
            # ClientDocument.number AS docNumber,
            # ClientDocument.serial AS docSerial,
            # ClientDocument.documentType_id AS docTypeId
        FROM
            Client
            # LEFT JOIN ClientDocument ON ClientDocument.id = getClientDocumentId(Client.id)
            INNER JOIN Event ON Event.client_id = Client.id
        WHERE
            Client.deleted = 0
            AND Event.deleted = 0
            AND DATE(Event.execDate) BETWEEN DATE('{begDate}') AND DATE('{endDate}')
        """.format(
            begDate=self.begDate.date().toString('yyyy-MM-dd'),
            endDate=self.endDate.date().toString('yyyy-MM-dd')
        )
        query = db.query(query)
        query.setForwardOnly(True)

        recordsCount = query.size()
        badRecordCount = 0
        processedRecordCount = 0
        self.progressBar.setMaximum(query.size())

        while query.next():
            QtGui.qApp.processEvents()
            if self.abort: break

            record = query.record()
            processedRecordCount += 1
            self.item_bad = False
            self.progressBar.setValue(processedRecordCount)

            self.client_id = self.itemId = forceInt(val('client_id'))

            fullName = forceString(val('fullName'))
            birthDate = forceDate(val('birthDate'))
            bd_err = ', ' + birthDate.toString('yyyy-MM-dd') if birthDate else ''

            self.err_str = 'client ' + forceString(self.client_id) + ' (' + fullName + bd_err + ') '

            self.checkDocument(self.client_id)

            if self.item_bad: badRecordCount += 1
            self.labelInfo.setText(u'%d клиентов всего; %d с ошибками' % (recordsCount, badRecordCount))

    def openItem(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            dialog.load(clientId)
            return dialog
        else:
            return None

    def checkDocument(self, client_id):
        document = getClientDocument(client_id)
        if document:
            # docId = forceRef(rec.value('docId'))
            serial = forceString(document.value('serial'))
            number = forceString(document.value('number'))
            documentTypeId = forceRef(document.value('documentType_id'))

            # if docId:
            # cond = 'serial=\'' + serial + '\' and number=\'' + number + '\''
            # if len(QtGui.qApp.db.getRecordList('ClientDocument', where=cond)) > 1:
            #     self.err2log(u'двойной документ ' + serial + ' ' + number)

            if not serial:
                self.err2log(u'отсутсвует серия документа ')

            if not number:
                self.err2log(u'отсутсвует номер документа ')

            if not documentTypeId:
                self.err2log(u'отсутсвует тип документа ')
        else:
            self.err2log(u'отсутствует документ')


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': '192.168.0.207',
        'port': 3306,
        'database': 's11vm2',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CClientDocumentsCheck(None)
    w.exec_()


if __name__ == '__main__':
    main()
