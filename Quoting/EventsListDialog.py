# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.CreateEvent  import editEvent
from Events.Utils        import EventIsPrimary, EventOrder
from Ui_EventsListDialog import Ui_EventsListDialog
from library.DialogBase  import CConstructHelperMixin
from library.TableModel  import CDateCol, CEnumCol, CRefBookCol, CTableModel, CTextCol
from library.Utils       import forceTr
from library.crbcombobox import CRBComboBox


class CEventsList(QtGui.QDialog, CConstructHelperMixin, Ui_EventsListDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.addModels('Events', CEventsTableModel(self))
        self.setModels(self.tblEvents, self.modelEvents, self.selectionModelEvents)


    def setClientId(self, clientId):
        db = QtGui.qApp.db
        cond = [u'Event.`deleted`=0',
                u'Event.`client_id` IN (%d)'%clientId,
                u"Event.`eventType_id` IN (SELECT id FROM EventType WHERE(EventType.purpose_id NOT IN (SELECT rbEventTypePurpose.id from rbEventTypePurpose where rbEventTypePurpose.code = '0')))"]
        table = db.table('Event')
        idList = db.getIdList(table,
                           'id',
                           cond,
                           ['setDate DESC', 'id'])
        self.tblEvents.setIdList(idList, None)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblEvents_doubleClicked(self, index):
        eventId = self.tblEvents.currentItemId()
        editEvent(self, eventId)


class CEventsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CDateCol(u'Назначен', ['setDate'],  10))
        self.addColumn(CDateCol(u'Выполнен', ['execDate'], 10))
        self.addColumn(CRefBookCol(u'Тип',  ['eventType_id'], 'EventType', 15))
        self.addColumn(CRefBookCol(forceTr(u'МЭС', u'TariffModel'),  ['MES_id'], 'mes.MES', 15, CRBComboBox.showCode))
        self.addColumn(CRefBookCol(u'Врач', ['execPerson_id'], 'vrbPersonWithSpeciality', 15))
        self.addColumn(CEnumCol(u'Первичный', ['isPrimary'], EventIsPrimary.nameList, 8))
        self.addColumn(CEnumCol(u'Порядок', ['order'], EventOrder().orderNameList, 8))
        # self.addColumn(CRefBookCol(u'Порядок', ['order'], 'rbEventOrder', 8))
        self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbResult', 40))
        self.addColumn(CTextCol(u'Внешний идентификатор', ['externalId'], 30))
        self.setTable('Event')
        self.diagnosisIdList = None