# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.ActionInfo import CActionInfo, CPropertyInfo
from Events.Utils import checkTissueJournalStatusByActions
from Registry.Utils import getClientInfo, formatClientBanner
from Resources.JobTicketReserveMixin import CJobTicketReserveMixin
from TissueJournal.TissueJournalModels import CActionRedactorModel, CPropertiesRedactorModel
from Ui_ActionTableRedactor import Ui_ActionTableRedactorDialog
from library.DialogBase import CDialogBase
from library.PrintInfo import CInfoContext, CInfoList
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.Utils import forceInt, forceString
from library.exception import CException


class CActionTableRedactor(CDialogBase, CJobTicketReserveMixin, Ui_ActionTableRedactorDialog):
    def __init__(self, parent, tissueJournalModel=None, onlyProperties=False):
        CDialogBase.__init__(self, parent)
        CJobTicketReserveMixin.__init__(self)
        self.setupUi(self)
        self._tissueJournalModel = tissueJournalModel
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        customizePrintButton(self.btnPrint, 'actionTableRedactor')
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        if onlyProperties:
            model = CPropertiesRedactorModel
        else:
            model = CActionRedactorModel
        self.addModels('ActionRedactor', model(self))
        self.setModels(self.tblActions, self.modelActionRedactor, self.selectionModelActionRedactor)
        self.setWindowTitleEx(u'Табличный редактор')
        self.setupDirtyCather()
        self._actionIdList = []
        self._mapIdToInfo = {}
        self._tissueRecordInfoById = {}
        self._currentClientId = None
        self.connect(self.btnPrint, QtCore.SIGNAL('printByTemplate(int)'), self.on_btnPrint_printByTemplate)
        self.connect(self.selectionModelActionRedactor,
                     QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                     self.on_selectionModelActionRedactor_currentChanged)

    def setTissueJournalIdList(self, tissueJournalIdList, actionIdList=None):
        self.setVerticalHeaderViewModeByTissueJournalIdCount(len(tissueJournalIdList))
        if actionIdList is None:
            db = QtGui.qApp.db
            table = db.table('Action')
            actionIdList = db.getIdList(table, 'id',
                                        table['takenTissueJournal_id'].inlist(tissueJournalIdList),
                                        table['takenTissueJournal_id'].name())
        self.setActionIdList(actionIdList, False)

    def setTissueRecordInfo(self, info):
        actionTypeTextInfo = self.modelActionRedactor.getActionTypeTextInfo(self.tblActions.currentIndex())
        if actionTypeTextInfo:
            info = info + u'\nТип действия: %s' % actionTypeTextInfo
        self.lblTissueJournalRecordInfo.setText(info)

    def setClientBanner(self, clientBanner):
        self.txtClientInfoBrowser.setHtml(clientBanner)

    def setClientBannerEx(self, id):
        if id != self._currentClientId:
            self._currentClientId = id
            clientInfo = self._mapIdToInfo.get(id, None)
            if not clientInfo:
                clientInfo = getClientInfo(id)
                self._mapIdToInfo[id] = clientInfo
            clientBanner = formatClientBanner(clientInfo)
            self.setClientBanner(clientBanner)

    def setActionIdList(self, actionIdList, checkTakenTissueCount=True):
        if checkTakenTissueCount:
            db = QtGui.qApp.db
            table = db.table('Action')
            cond = [table['id'].inlist(actionIdList)]
            record = db.getRecordEx(table, 'COUNT(DISTINCT takenTissueJournal_id) AS tissueJournalIdCount', cond)
            tissueJournalIdCount = forceInt(record.value('tissueJournalIdCount')) if record else 0
            self.setVerticalHeaderViewModeByTissueJournalIdCount(tissueJournalIdCount)
        self._actionIdList = actionIdList
        self.modelActionRedactor.setActionIdList(actionIdList)
        self.tblActions.setFocus(QtCore.Qt.OtherFocusReason)
        self.tblActions.setCurrentIndex(self.modelActionRedactor.firstAvailableIndex())

    def setVerticalHeaderViewModeByTissueJournalIdCount(self, tissueJournalIdCount):
        if tissueJournalIdCount > 1:
            self.modelActionRedactor.setVerticalHeaderViewIdentifiersMode()
        else:
            self.modelActionRedactor.setVerticalHeaderViewActionTypeMode()

    def setClientId(self, clientId):
        self.modelActionRedactor.setClientId(clientId)

    def formatTissueRecordInfo(self, id):
        rows = self._tissueRecordInfoById.setdefault(id, [])
        if not rows:
            if self._tissueJournalModel:
                model = self._tissueJournalModel
                modelIdList = model.idList()
                if id in modelIdList:
                    row = modelIdList.index(id)
                else:
                    return ''
                tissueType = forceString(model.data(model.index(row, 2)))
                identifier = forceString(model.data(model.index(row, 3)))
                status = forceString(model.data(model.index(row, 4)))
                date = forceString(model.data(model.index(row, 5)))
            else:
                db = QtGui.qApp.db
                record = db.getRecord('TakenTissueJournal',
                                      'tissueType_id, externalId, status, datetimeTaken',
                                      id)
                tissueType = forceString(db.translate('rbTissueType', 'id', record.value('tissueType_id'), 'name'))
                identifier = forceString(record.value('externalId'))
                status = [u'В работе',
                          u'Начато',
                          u'Ожидание',
                          u'Закончено',
                          u'Отменено',
                          u'Без резуьтата'][forceInt(record.value('status'))]
                date = forceString(record.value('datetimeTaken'))
            rows.append(u'Тип биоматериала: %s' % tissueType)
            rows.append(u'Идентификатор: %s' % identifier)
            rows.append(u'Статус: %s' % status)
            rows.append(u'Дата забора: %s' % date)
        return u', '.join(rows)

    def exec_(self):
        QtGui.qApp.setJTR(self)
        self.loadDialogPreferences()
        self.setWindowState(QtCore.Qt.WindowMaximized)
        result = QtGui.QDialog.exec_(self)
        try:
            if not result:
                self.delAllJobTicketReservations()
        except:
            QtGui.qApp.logCurrentException()
        QtGui.qApp.setJTR(None)
        return result

    def saveData(self):
        QtGui.qApp.callWithWaitCursor(self, self.save)
        return True

    def save(self):
        listForTissueJournalStatusChecking = self.modelActionRedactor.saveItems()
        for actionItem, propertiesDictItem in self.modelActionRedactor.itemsForDeleting():
            actionRecord = actionItem.getRecord()
            actionRecord.setValue('deleted', QtCore.QVariant(1))
            QtGui.qApp.db.updateRecord('Action', actionRecord)
        checkTissueJournalStatusByActions(listForTissueJournalStatusChecking)

    def getClientIdByTakenTissueJournalId(self, takenTissueJournalId):
        return self.modelActionRedactor.getClientIdByTakenTissueJournalId(takenTissueJournalId)

    #    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        context = CInfoContext()
        actionsInfo = context.getInstance(CActionTableRedactorInfoList, tuple(self._actionIdList))
        data = {'actions': actionsInfo}
        applyTemplate(self, templateId, data)

    #    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelActionRedactor_currentChanged(self, current, previous):
        row = current.row()
        previousRow = previous.row()
        if previousRow != row:
            takenTissueJournalId = self.modelActionRedactor.getTakenTissueJournalId(row)
            self.setTissueRecordInfo(self.formatTissueRecordInfo(takenTissueJournalId))
            self.setClientBannerEx(self.getClientIdByTakenTissueJournalId(takenTissueJournalId))


# ###################################################################
class CActionTableRedactorInfo(CActionInfo):
    def isVisible(self, propertyType):
        return propertyType.visibleInTableRedactor == 1  # видно в тадличном редакторе и редактрируемо

    def __getitem__(self, key):
        if isinstance(key, (basestring, QtCore.QString)):
            try:
                property = self._action.getProperty(unicode(key))
                propertyType = property.type()
                if self.isVisible(propertyType):
                    return self.getInstance(CPropertyInfo, property)
                else:
                    actionType = self._action.getType()
                    raise CException(u'У действия типа "%s" свойство "%s" не выводится в табличном редакторе' % (
                        actionType.name, unicode(key))
                                     )
            except KeyError:
                actionType = self._action.getType()
                raise CException(u'Действие типа "%s" не имеет свойства "%s"' % (actionType.name, unicode(key)))
        if isinstance(key, (int, long)):
            try:
                return self.getInstance(CPropertyInfo, self._action.getPropertyByIndex(key))
            except IndexError:
                actionType = self._action.getType()
                raise CException(
                    u'Действие типа "%s" не имеет свойства c индексом "%s"' % (actionType.name, unicode(key))
                )
        else:
            raise TypeError, u'Action property subscription must be string or integer'

    def __iter__(self):
        for property in self._action.getProperties():
            if self.isVisible(property.type()):
                yield self.getInstance(CPropertyInfo, property)


class CActionTableRedactorInfoList(CInfoList):
    def __init__(self, context, idList):
        CInfoList.__init__(self, context)
        self._idList = idList

    def _load(self):
        self._items = [self.getInstance(CActionTableRedactorInfo, id) for id in self._idList]
        return True
