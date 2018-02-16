# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from DataCheck.CCheck import CCheck
from Events.Utils import getRealPayed, getEventFinanceId, getWorkEventTypeFilter
from Orgs.OrgComboBox import CContractDbData, CContractDbModel
from Registry.Utils import getClientWork
from library.DialogBase import CDialogBase
from library.Utils import forceRef, forceInt, forceDate, calcAgeTuple, forceString

from Ui_EventServicesCheckDialog import Ui_EventServiceCheckDialog


class CEventServicesCheck(CDialogBase, Ui_EventServiceCheckDialog, CCheck):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        CCheck.__init__(self)
        self.tblEventType.setTable('EventType', filter=getWorkEventTypeFilter())

        self.contractServices = {}
        self.eventTypeMap = {}

    def getContractServices(self, contractId):
        db = QtGui.qApp.db
        CT = db.table('Contract_Tariff')
        return set(db.getIdList(CT, CT['service_id'], [CT['master_id'].eq(contractId),
                                                       CT['deleted'].eq(0)]))

    def checkEvent(self, eventId, contractId):
        if contractId in self.contractServices:
            services = self.contractServices[contractId]
        else:
            services = self.getContractServices(contractId)
            self.contractServices[contractId] = services

        db = QtGui.qApp.db
        Action = db.table('Action')
        ActionType = db.table('ActionType')
        ActionTypeService = db.table('ActionType_Service')
        Service = db.table('rbService')
        Visit = db.table('Visit')

        table = Action.innerJoin(ActionType, [ActionType['id'].eq(Action['actionType_id']), ActionType['deleted'].eq(0)])
        table = table.innerJoin(ActionTypeService, [ActionTypeService['master_id'].eq(ActionType['id'])])

        actionCond = [
            Action['event_id'].eq(eventId),
            Action['deleted'].eq(0),
            ActionType['class'].inlist([1, 2])
        ]
        actionServices = db.getRecordList(table, [Action['id'].alias('actionId'), ActionTypeService['service_id'].alias('serviceId')], actionCond, order=Action['id'])
        for rec in actionServices:
            actionId = forceRef(rec.value('actionId'))
            serviceId = forceRef(rec.value('serviceId'))
            if serviceId not in services:
                self.err2log(u'посещение {0}: услуги {1} нет в договоре'.format(actionId, forceString(db.translate(Service, 'id', serviceId, 'concat_ws(\'|\', code, name)'))))

        visitServices = db.getRecordList(Visit, [Visit['id'].alias('visitId'), Visit['service_id'].alias('serviceId')],
                                         [Visit['event_id'].eq(eventId), Visit['deleted'].eq(0)], order=Visit['id'])
        for rec in visitServices:
            visitId = forceRef(rec.value('visitId'))
            serviceId = forceRef(rec.value('serviceId'))
            if serviceId not in services:
                self.err2log(u'мероприятие {0}: услуги {1} нет в договоре'.format(visitId, forceString(db.translate(Service, 'id', serviceId, 'concat_ws(\'|\', code, name)'))))

    def check(self):
        db = QtGui.qApp.db
        Event = db.table('Event')

        dateFrom = self.edtDateFrom.date()
        dateTo = self.edtDateTo.date()
        eventTypeIdList = self.tblEventType.values()

        eventCond = [Event['deleted'].eq(0),
                     Event['setDate'].dateGe(dateFrom),
                     Event['setDate'].dateLe(dateTo),
                     Event['contract_id'].isNotNull()]

        if eventTypeIdList:
            eventCond.append(Event['eventType_id'].inlist(eventTypeIdList))
        events = db.getRecordList(Event, where=eventCond)

        self.progressBar.setMaximum(len(events) - 1)

        for i, eventRecord in enumerate(events):
            QtGui.qApp.processEvents()
            if self.abort:
                break

            eventId = forceRef(eventRecord.value('id'))
            eventTypeId = forceRef(eventRecord.value('eventType_id'))
            self.eventTypeMap[eventId] = eventTypeId
            contractId = forceRef(eventRecord.value('contract_id'))

            self.progressBar.setValue(i)
            self.itemId = eventId
            self.item_bad = False
            self.err_str = u'Обращение {0}: '.format(eventId)

            self.checkEvent(eventId, contractId)


    def openItem(self, eventId):
        eventTypeId = self.eventTypeMap.get(eventId)
        formClass = self.getEventFormClass(eventTypeId)
        form = formClass(self)
        form.load(eventId)
        return form

def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 230493

    QtGui.qApp.db = connectDataBaseByInfo({
        'driverName' :      'mysql',
        'host' :            '192.168.0.207',
        'port' :            3306,
        'database' :        'most03-06-2016',
        'user':             'dbuser',
        'password':         'dbpassword',
        'connectionName':   'vista-med',
        'compressData' :    True,
        'afterConnectFunc': None
    })

    CEventServicesCheck(None).exec_()


if __name__ == '__main__':
    main()