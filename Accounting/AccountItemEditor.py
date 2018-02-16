# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################


"""
Created on 13/03/15

@author: atronah
"""

from PyQt4 import QtGui, QtCore
from Ui_AccountItemEditor import Ui_Dialog

from library.DialogBase import CDialogBase
from library.TableModel import CCol
from library.Utils import forceRef, forceString, forceStringEx, forceDouble,forceDecimal


class CAccountItemEditor(CDialogBase, Ui_Dialog):
    ServiceSource = 0
    ActionSource = 1
    VisitSource = 2
    EventSource = 3

    def __init__(self, parent, db, eventCache, visitCache, actionCache, serviceCache):
        super(CAccountItemEditor, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(u'Редактирование элемента счета')

        self._db = db
        self.eventCache  = eventCache
        self.visitCache  = visitCache
        self.actionCache = actionCache
        self.serviceCache = serviceCache

        self.cmbUnit.setTable(u'rbMedicalAidUnit')

        self._itemId = None

        self.cmbService.currentIndexChanged.connect(self.updateServiceName)
        self.accountIdList = []
        self.accountNameList = []
        self.initCmbAccounts()


    def getServiceName(self, record):
        serviceId = forceRef(record.value('service_id'))
        name = CCol.resolveValueByCaches(serviceId, [(self.serviceCache, 'name')])
        if name != CCol.invalid:
            return name, self.ServiceSource

        actionId = forceRef(record.value('action_id'))
        name = CCol.resolveValueByCaches(actionId, [(self.actionCache, 'actionType_id'),
                                                   (self.actionTypeCache, 'name')])
        if name != CCol.invalid:
            return name, self.ActionSource

        visitId = forceRef(record.value('visit_id'))
        name = CCol.resolveValueByCaches(visitId, [(self.visitCache, 'service_id'),
                                                   (self.serviceCache, 'name')])
        if name != CCol.invalid:
            return name, self.VisitSource

        eventId = forceRef(record.value('event_id'))
        name = CCol.resolveValueByCaches(eventId, [(self.eventCache, 'eventType_id'),
                                                   (self.eventTypeCache, 'name')])
        return name, self.EventSource



    def setRecord(self, record):
        self._itemId = forceRef(record.value(u'id'))

        serviceId = forceRef(record.value(u'service_id'))
        self.cmbService.setValue(serviceId)

        self.edtPrice.setValue(forceDecimal(record.value(u'price')))
        self.edtAmount.setValue(forceDecimal(record.value(u'amount')))
        self.edtSum.setValue(forceDecimal(record.value(u'sum')))
        self.cmbUnit.setValue(u'unit_id')
        self.edtUET.setValue(forceDecimal(record.value(u'uet')))

        if serviceId is None:
            otherName, otherSource = forceString(self.getServiceName(record))
            otherSourceName = {self.EventSource: u'Событие',
                               self.ActionSource: u'Действие',
                               self.VisitSource: u'Посещение',
                               self.ServiceSource: u'Услуга'}.get(otherSource, u'')
            if otherSourceName and otherName != CCol.invalid:
                self.lblServiceNameSource.setText(otherSourceName)
                self.lblServiceName.setText(otherName)
        masterId = forceRef(QtGui.qApp.db.translate(u'Account_Item', u'id', self._itemId, u'master_id'))
        self.cmbAccount.setCurrentIndex(self.accountIdList.index(masterId))


    def saveData(self):
        if self._itemId:
            table = self._db.table(u'Account_Item')
            record = table.newRecord([u'id',
                                      u'service_id',
                                      u'price',
                                      u'amount',
                                      u'uet',
                                      u'sum',
                                      u'unit_id',
                                      u'master_id'])

            record.setValue(u'id', QtCore.QVariant(self._itemId))
            record.setValue(u'service_id', QtCore.QVariant(self.cmbService.value()))
            record.setValue(u'price', QtCore.QVariant(self.edtPrice.value()))
            record.setValue(u'amount', QtCore.QVariant(self.edtAmount.value()))
            record.setValue(u'uet', QtCore.QVariant(self.edtUET.value()))
            record.setValue(u'sum', QtCore.QVariant(self.edtSum.value()))
            record.setValue(u'unit_id', QtCore.QVariant(self.cmbUnit.value()))
            record.setValue(u'master_id', QtCore.QVariant(self.accountIdList[self.cmbAccount.currentIndex()]))

            self._db.updateRecord(table, record)
            return True
        return False

    def initCmbAccounts(self):
        db = QtGui.qApp.db
        tblAccount = db.table('Account')
        cols = [tblAccount['id'], tblAccount['number'], tblAccount['date']]
        records = db.getRecordList(tblAccount, cols, tblAccount['deleted'].eq(0),
                                   [tblAccount['date'], tblAccount['number']])
        self.accountIdList = []
        self.accountNameList = []
        for record in records:
            self.accountIdList.append(forceRef(record.value('id')))
            number = forceStringEx(record.value('number'))
            date = forceStringEx(record.value('date'))
            self.accountNameList.append(u'%s от %s' % (number, date))
            self.cmbAccount.addItem(u'%s от %s' % (number, date))

    @QtCore.pyqtSlot()
    def updateServiceName(self):
        serviceId = self.cmbService.value()
        if serviceId:
            sourceName = u'Услуга'
            name = forceString(CCol.resolveValueByCaches(serviceId, [(self.serviceCache, 'name')]))
        else:
            sourceName = u''
            name = u''
        self.lblServiceNameSource.setText(sourceName)
        self.lblServiceName.setText(name)





def main():
    import sys
    app = QtGui.QApplication(sys.argv)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()