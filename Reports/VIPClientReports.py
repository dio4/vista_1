# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils           import getWorkEventTypeFilter
from Reports.ReportLeavedClients import CLeavedClients
from library.Utils          import forceDouble, forceInt, forceString, forceDateTime
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportPeriodontist  import Ui_ReportPeriodontist


class CReportVIPClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сводка по VIP пациентам')

    def getSetupDialog(self, parent):
        result = CLeavedClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        def selectData(params):
            begDate = params.get('begDate', None).toString(QtCore.Qt.ISODate)
            endDate = params.get('endDate', None).toString(QtCore.Qt.ISODate)

            db = QtGui.qApp.db

            tableClientVIP = db.table('ClientVIP')

            cond = [
                tableClientVIP['createDatetime'].dateLe(endDate),
                tableClientVIP['createDatetime'].dateGe(begDate)
            ]

            stmt = u'''
                SELECT
                    Client.clientName,
                    ClientVIP.createDatetime,
                    Person.name,
                    ClientVIP.comment,
                    'ВЫСТАВЛЕН' AS status
                FROM vrbClientInfo AS Client
                    INNER JOIN ClientVIP ON Client.id = ClientVIP.client_id AND ClientVIP.deleted = 0
                    INNER JOIN vrbPersonWithSpeciality AS Person ON Person.id = ClientVIP.createPerson_id
                WHERE
                    %s
            ''' % db.joinAnd(cond)

            return db.query(stmt)

        # detailPerson = params.get('detailPerson', False)

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
            ('%2', [u'№ п/п'], CReportBase.AlignRight),
            ('%30', [u'Фамилия, Имя, Отчество'], CReportBase.AlignLeft),
            ('%5', [u'VIP'], CReportBase.AlignLeft),
            ('%5', [u'Проставивший статус'], CReportBase.AlignLeft),
            ('%5', [u'Дата проставления'], CReportBase.AlignLeft),
            ('%5', [u'Комментарий'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()

            clientName = forceString(record.value('clientName'))
            createDatetime = forceDateTime(record.value('createDatetime')).toString('dd.MM.yyyy hh:mm')
            personName = forceString(record.value('name'))
            comment = forceString(record.value('comment'))
            status = forceString(record.value('status'))

            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, clientName)
            table.setText(i, 2, status)
            table.setText(i, 3, personName)
            table.setText(i, 4, createDatetime)
            table.setText(i, 5, comment)

        return doc


class CReportVIPClientsDetalization(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Детализация по VIP пациентам')

    def getSetupDialog(self, parent):
        result = CLeavedClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        def getUserIdList(params):
            begDate = params.get('begDate', None).toString(QtCore.Qt.ISODate)
            endDate = params.get('endDate', None).toString(QtCore.Qt.ISODate)

            db = QtGui.qApp.db

            tableClientVIP = db.table('ClientVIP')

            cond = [
                tableClientVIP['createDatetime'].dateLe(endDate),
                tableClientVIP['createDatetime'].dateGe(begDate)
            ]

            stmt = u'''
                    SELECT
                        Client.clientName,
                        ClientVIP.createDatetime,
                        Person.name,
                        ClientVIP.comment,
                        'ВЫСТАВЛЕН' AS status
                    FROM vrbClientInfo AS Client
                        INNER JOIN ClientVIP ON Client.id = ClientVIP.client_id
                        INNER JOIN vrbPersonWithSpeciality AS Person ON Person.id = ClientVIP.createPerson_id
                    WHERE
                        %s
                ''' % db.joinAnd(cond)

            return db.query(stmt)

        def selectData(params):
            begDate = params.get('begDate', None).toString(QtCore.Qt.ISODate)
            endDate = params.get('endDate', None).toString(QtCore.Qt.ISODate)

            db = QtGui.qApp.db

            tableClientVIP = db.table('ClientVIP')

            cond = [
                tableClientVIP['createDatetime'].dateLe(endDate),
                tableClientVIP['createDatetime'].dateGe(begDate)
            ]

            stmt = u'''
                SELECT
                    Client.id AS clientId,
                    Client.clientName,
                    ClientVIP.createDatetime,
                    Person.name,
                    ClientVIP.comment,
                    IF(ClientVIP.deleted = 0, 'ВЫСТАВЛЕН', 'СНЯТ') AS status
                FROM vrbClientInfo AS Client
                    INNER JOIN ClientVIP ON Client.id = ClientVIP.client_id
                    INNER JOIN vrbPersonWithSpeciality AS Person ON Person.id = ClientVIP.createPerson_id
                WHERE
                    %s
            ''' % db.joinAnd(cond)

            return db.query(stmt)

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
            ('%2', [u'№ п/п'], CReportBase.AlignRight),
            ('%30', [u'Фамилия, Имя, Отчество'], CReportBase.AlignLeft),
            ('%5', [u'VIP'], CReportBase.AlignLeft),
            ('%5', [u'Проставивший статус'], CReportBase.AlignLeft),
            ('%5', [u'Дата проставления'], CReportBase.AlignLeft),
            ('%5', [u'Комментарий'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        prevRecord = {
            'prevClientId': None,
            'row': None
        }
        rowNumber = 1
        insertMainData = True
        while query.next():
            record = query.record()

            if prevRecord['prevClientId'] is None:
                prevRecord['prevClientId'] = forceInt(record.value('clientId'))
                prevRecord['row'] = 1

            currentClientId = forceInt(record.value('clientId'))
            clientName = forceString(record.value('clientName'))
            createDatetime = forceDateTime(record.value('createDatetime')).toString('dd.MM.yyyy hh:mm')
            personName = forceString(record.value('name'))
            comment = forceString(record.value('comment'))
            status = forceString(record.value('status'))

            i = table.addRow()

            if prevRecord['prevClientId'] != currentClientId:
                table.mergeCells(prevRecord['row'], 1, i - prevRecord['row'], 1)
                table.mergeCells(prevRecord['row'], 0, i - prevRecord['row'], 1)

                prevRecord['prevClientId'] = currentClientId
                prevRecord['row'] = i
                rowNumber += 1
                insertMainData = True

            if insertMainData:
                table.setText(i, 0, rowNumber)
                table.setText(i, 1, clientName)
                insertMainData = False

            table.setText(i, 2, status)
            table.setText(i, 3, personName)
            table.setText(i, 4, createDatetime)
            table.setText(i, 5, comment)

        return doc
