# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import codecs

from PyQt4                  import QtGui, QtCore

from Events.Action          import CAction, CActionType
from Events.EventInfo       import CEventInfo
from Events.Utils           import getEventType

from Orgs.PersonInfo        import CPersonInfo

from Registry.Utils         import getClientBanner, getClientInfo2

from library.constants      import atcHome, etcTimeTable
from library.DialogBase     import CDialogBase
from library.PrintTemplates import applyTemplate, getPrintTemplates, applyTemplateInt
from library.TableModel     import CTableModel, CDateTimeFixedCol, CEnumCol, CRefBookCol, CTextCol
from library.Utils          import forceDate, forceInt, forceRef, forceString, forceTime

from Ui_BeforeRecordClient  import Ui_Dialog


class CQueue(CDialogBase, Ui_Dialog):
    def __init__(self, parent, clientId, actionIdList, visibleOkButton = False):
        CDialogBase.__init__(self, parent)
        cols = [
            CDateTimeFixedCol(u'Дата и время приема', ['directionDate'], 20),
            CRefBookCol(u'Тип',         ['actionType_id'], 'ActionType', 15),
            CEnumCol(u'Состояние',      ['status'], CActionType.retranslateClass(False).statusNames, 4),
            CRefBookCol(u'Назначил',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20),
            CRefBookCol(u'Специалист',  ['person_id'], 'vrbPersonWithSpeciality', 20),
            CTextCol(u'Каб',            ['office'], 6),
            CTextCol(u'Примечания',     ['note'], 6),
        ]
        self.addModels('Actions', CTableModel(self, cols, 'Action'))
        self.btnPrint = QtGui.QPushButton(u'Печать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        if visibleOkButton:
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        else:
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.tblActions.setModel(self.modelActions)
        self.tblActions.addPopupPrintRow(self)
        self.clientId = clientId
        self.txtClientInfoBrowser.setHtml(getClientBanner(self.clientId) if self.clientId else '')
        self.modelActions.setIdList(actionIdList)
        self.buttonBox.setEnabled(bool(actionIdList))


    def showQueuePosition(self, actionId):
        if actionId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tablePerson = db.table('Person')
            cols = [tableAction['directionDate'],
                    tableAction['person_id'],
                    tablePerson['orgStructure_id'],
                    tablePerson['speciality_id']]
            cond = [tableAction['id'].eq(actionId),
                    tableAction['deleted'].eq(0),
                    tablePerson['deleted'].eq(0)]
            table = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
            record = db.getRecordEx(table, cols, cond)
            if record:
                date = forceDate(record.value('directionDate'))
                personId = forceRef(record.value('person_id'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                specialityId = forceRef(record.value('speciality_id'))
                try:
                    if QtGui.qApp.mainWindow.dockResources and personId and date and orgStructureId and specialityId and actionId:
                        QtGui.qApp.mainWindow.dockResources.content.showQueueItem(orgStructureId, specialityId, personId, date, actionId)
                except:
                    pass


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActions_doubleClicked(self, index):
        actionId = self.tblActions.currentItemId()
        if actionId:
            self.showQueuePosition(actionId)

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        if self.modelActions.rowCount():
            self.tblActions.setReportHeader(u'Протокол предварительной записи пациента')
            self.tblActions.setReportDescription(self.txtClientInfoBrowser.toHtml())
            self.tblActions.printContent()


    def printOrderQueueItem(self):
        def getTimeRange(actionTypeCode, date, personId):
            timeRange = ('--:--', '--:--')
            db = QtGui.qApp.db
            eventTypeId = getEventType(etcTimeTable).eventTypeId
            eventTable = db.table('Event')
            cond = [eventTable['deleted'].eq(0),
                    eventTable['eventType_id'].eq(eventTypeId),
                    eventTable['execDate'].eq(date),
                    eventTable['execPerson_id'].eq(personId)
                   ]
            event = db.getRecordEx(eventTable, '*', cond)
            if event:
                eventId = forceRef(event.value('id'))
                action = CAction.getAction(eventId, actionTypeCode)
                begTime = action['begTime']
                endTime = action['endTime']
                if begTime and endTime:
                    timeRange = begTime.toString('H:mm') + ' - ' + endTime.toString('H:mm')
            return timeRange
        actionId = self.tblActions.currentItemId()
        record = self.tblActions.currentItem()
        db = QtGui.qApp.db
        tableActionProperty_Action = db.table('ActionProperty_Action')
        tableActionProperty = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        table = tableActionProperty_Action.leftJoin(tableActionProperty, tableActionProperty['id'].eq(tableActionProperty_Action['id']))
        table = table.leftJoin(tableAction,     tableAction['id'].eq(tableActionProperty['action_id']))
        table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        cond = [tableAction['deleted'].eq(0),
                tableActionProperty['deleted'].eq(0),
                tableActionType['deleted'].eq(0),
                tableActionProperty_Action['value'].eq(actionId)
                ]
        date = forceDate(record.value('directionDate'))
        time = forceTime(record.value('directionDate'))
        office = forceString(record.value('office'))
        personId = forceString(record.value('person_id'))
        record = db.getRecordEx(table, [tableActionType['code'], tableActionProperty_Action['index']], cond)
        if record:
            code = forceString(record.value('code'))
            index = forceInt(record.value('index'))
            if self.clientId:
                printOrder(self.clientId,
                                   code == atcHome,
                                   date,
                                   office,
                                   personId,
                                   index + 1,
                                   time,
                                   getTimeRange(code, date, personId))


def printOrder(widget, clientId, toHome, date, office, personId, eventId, num, time, timeRange):
    if toHome:
        contextName = 'orderHome'
        typeText = u'Вызов на дом'
    else:
        contextName = 'orderAmb'
        typeText = u'Направление на приём к врачу'
    visitInfo  = {'clientId' : clientId,
                  'type'     : typeText,
                  'date'     : forceString(date),
                  'office'   : office,
                  'personId' : personId,
                  'num'      : num,
                  'time'     : time.toString('H:mm') if time else '--:--',
                  'timeRange': timeRange,
                 }
    clientInfo = getClientInfo2(clientId)
    personInfo = clientInfo.getInstance(CPersonInfo, personId)
    eventInfo = clientInfo.getInstance(CEventInfo, eventId)
    
    data = {'event':eventInfo, 'client':clientInfo, 'person':personInfo, 'visit': visitInfo}
    templates = getPrintTemplates(contextName)
    if templates:
        templateId = templates[0][1]
        QtGui.qApp.call(widget, applyTemplate, (widget, templateId, data))
    else:
        orderTemplate = getOrderTemplate()
        QtGui.qApp.call(widget, applyTemplateInt, (widget, visitInfo['type'], orderTemplate, data))


def getOrderTemplate():
    import os.path
    templateFileName   = 'order.html'
    fullPath = os.path.join(QtGui.qApp.getTemplateDir(), templateFileName)
    for enc in ['utf-8', 'cp1251']:
        try:
            file = codecs.open(fullPath, encoding=enc, mode='r')
            return file.read()
        except:
            pass
    return \
        u'<HTML><BODY>' \
        u'код: {client.id}&nbsp;<FONT FACE="Code 3 de 9" SIZE=+3>*{client.id}*</FONT><BR/>' \
        u'ФИО: <B>{client.fullName}</B><BR/>' \
        u'ДР:  <B>{client.birthDate}</B>(<B>{client.age}</B>),&nbsp;Пол: <B>{client.sex}</B>,&nbsp;СНИЛС:<B>{client.SNILS}</B><BR/>' \
        u'Док: <B>{client.document}</B><BR/>' \
        u'Полис:<B>{client.policy}</B><BR/>' \
        u'<HR>' \
        u'<CENTER>{visit.type}</CENTER>' \
        u'<HR>' \
        u'Врач: <B>{person.fullName}</B>(<B>{person.speciality}</B>)<BR>' \
        u'Явиться: <B>{visit.date} в каб.{visit.office}</B> Приём<B>{visit.timeRange}</B><BR>' \
        u'Время: <B>{visit.time}, #{visit.num}</B>' \
        u'</BODY></HTML>'
