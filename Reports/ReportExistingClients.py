# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceBool, forceString
from Orgs.Utils import getOrgStructureDescendants

from Ui_ReportExistingClients import Ui_Dialog


class RecordSimulator(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def value(self, key):
        return super(RecordSimulator, self).__getitem__(key)


class QueryResultSimulator(list):
    def __init__(self, *args, **kwargs):
        list.__init__(*args, **kwargs)
        self._iterlist = iter(self)
        self._item = None

    def next(self):
        try:
            self._item = next(self._iterlist)
            return True
        except StopIteration:
            return False

    def append(self, p_object):
        super(QueryResultSimulator, self).append(p_object)
        self._iterlist = iter(self)

    def record(self):
        return self._item


def selectData(params):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableOrgMoving = db.table('ActionProperty_Organisation').alias('orgMoving')

    eventTypeIds = (params.get('chkEventType'), params.get('eventTypeId'), params.get('eventTypeIdMulti'))
    orgStructureIds = (params.get('chkOrgStructure'), params.get('orgStructureId'), params.get('orgStructureIdMulti'))
    days = params.get('days')

    cond = []

    if not eventTypeIds[0] and eventTypeIds[1]:
        cond.append(tableEvent['eventType_id'].eq(eventTypeIds[1]))
    elif eventTypeIds[0] and eventTypeIds[2]:
        cond.append(tableEvent['eventType_id'].inlist(eventTypeIds[2]))
    if not orgStructureIds[0] and orgStructureIds[1]:
        cond.append(tableOrgMoving['value'].inlist(getOrgStructureDescendants(orgStructureIds[1])))
    elif orgStructureIds[0] and orgStructureIds[2]:
        cond.append(tableOrgMoving['value'].inlist(orgStructureIds[2]))
    if days:
        cond.append(('datediff(CURDATE(), Event.setDate) >= %s' % days))

    stmt = u'''SELECT  Client.lastName AS LastName
                     , Client.firstName AS FirstName
                     , Client.patrName AS PatrName
                     , Event.externalId AS IB
                     , if(datediff(CURDATE(), Event.setDate) = 0, 1, datediff(CURDATE(), Event.setDate)) AS Days
                     , Client.id AS id
            FROM
              Client
                INNER JOIN Event
                    ON Client.id = Event.client_id
                        AND Event.deleted = 0

                INNER JOIN ActionType MovingActionType
                    ON MovingActionType.deleted = 0
                        AND MovingActionType.flatCode = 'moving'

                INNER JOIN Action MovingAction
                    ON  MovingAction.event_id = Event.id
                        AND MovingAction.deleted = 0
                        AND MovingAction.actionType_id = MovingActionType.id
                        AND MovingAction.status = 0

                INNER JOIN ActionPropertyType MovingActionPropertyType
                    ON MovingActionPropertyType.actionType_id = MovingActionType.id
                    AND MovingActionPropertyType.name LIKE 'Отделение пребывания%%'
                INNER JOIN ActionProperty MovingActionProperty
                    ON  MovingActionProperty.action_id = MovingAction.id
                        AND MovingActionProperty.type_id = MovingActionPropertyType.id
                INNER JOIN ActionProperty_OrgStructure orgMoving
                    ON orgMoving.id = MovingActionProperty.id

            %s

            ORDER BY
              Days DESC, IB''' % ((u'WHERE ' + db.joinAnd(cond)) if cond else u'')

    return db.query(stmt)


class CReportExistingClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет о продолжительности пребывания')

    def getSetupDialog(self, parent):
        result = CExistingClients(parent)
        result.setWindowTitle(self.title())
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
        tableColumns = (('N', ('2%', [u'№'], CReportBase.AlignLeft)),
                        ('IB', ('10%', [u'№ ИБ'], CReportBase.AlignLeft)),
                        ('LastName', ('20%', [u'Фамилия'], CReportBase.AlignLeft)),
                        ('FirstName', ('20%', [u'Имя'], CReportBase.AlignLeft)),
                        ('PatrName', ('20%', [u'Отчество'], CReportBase.AlignLeft)),
                        ('Days', ('10%', [u'Кол-во койко-дней'], CReportBase.AlignLeft)))
        table = createTable(cursor, map(lambda item: item[1], tableColumns))

        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row_ind = table.addRow()
            for col_ind, (name, col) in enumerate(tableColumns):
                if name == 'N':
                    table.setText(row_ind, col_ind, str(row_ind))
                else:
                    table.setText(row_ind, col_ind, forceString(record.value(name)))

        return doc


class CExistingClients(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbEventType.setCurrentIndex(0)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.lstEventType.setTable('EventType', filter=getWorkEventTypeFilter())
        self.lstEventType.setVisible(False)
        self.lstOrgStructure.setTable('OrgStructure')
        self.lstOrgStructure.setVisible(False)
        self.edtDays.setValidator(QtGui.QIntValidator(self))

    def setParams(self, params):
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.lstEventType.setValues(params.get('eventTypeIdMulti', []))
        self.lstOrgStructure.setValues(params.get('orgStructureIdMulti', []))
        self.chkEventTypeMulti.setChecked(forceBool(params.get('chkEventType', False)))
        self.chkOrgStructureMulti.setChecked(forceBool(params.get('chkOrgStructure', False)))
        self.edtDays.setText(params.get('days', ''))
        self.on_chkEventTypeMulti_clicked(self.chkEventTypeMulti.isChecked())
        self.on_chkOrgStructureMulti_clicked(self.chkOrgStructureMulti.isChecked())

    def params(self):
        params = dict()
        params['eventTypeId'] = self.cmbEventType.value()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['eventTypeIdMulti'] = self.lstEventType.nameValues()
        params['chkEventType'] = self.chkEventTypeMulti.isChecked()
        params['orgStructureIdMulti'] = self.lstOrgStructure.nameValues()
        params['chkOrgStructure'] = self.chkOrgStructureMulti.isChecked()
        params['days'] = self.edtDays.text()
        return params

    @QtCore.pyqtSlot(bool)
    def on_chkEventTypeMulti_clicked(self, checked):
        self.lstEventType.setVisible(checked)
        self.cmbEventType.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructureMulti_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)