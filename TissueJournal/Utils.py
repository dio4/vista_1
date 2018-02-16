# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Events.Action                  import CAction
from Events.Utils                   import getExternalIdDateCond

from library.crbcombobox            import CRBComboBox
from library.DialogBase             import CDialogBase
from library.ProgressBar            import CProgressBar
from library.Utils                  import forceDouble, forceInt, forceRef, forceString, forceStringEx, smartDict

from Ui_TissueJournalTotalEditor    import Ui_TissueJournalTotalEditorDialog

probeIsFinished = 3

class CClientIdentifierSelector(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.vLayout = QtGui.QVBoxLayout()
        self.lblTitle = QtGui.QLabel(u'Значение', self)
        self.vLayout.addWidget(self.lblTitle)
        self.cmbIdentifierTypes = QtGui.QComboBox(self)
        self.vLayout.addWidget(self.cmbIdentifierTypes)
        self.lblOrderBy = QtGui.QLabel(u'Сортировка:', self)
        self.vLayout.addWidget(self.lblOrderBy)
        self.cmbOrderBy = QtGui.QComboBox(self)
        self.cmbOrderBy.addItems([u'по ИБМ', u'по ФИО'])
        self.vLayout.addWidget(self.cmbOrderBy)

        self.chkNeedAmountAndUnit = QtGui.QCheckBox(u'Печатать \'Кол-во биоматериала\' и \'Ед.изм.\'', self)
        self.chkNeedStatus   = QtGui.QCheckBox(u'Печатать \'Статус\'', self)
        self.chkNeedDatetime = QtGui.QCheckBox(u'Печатать \'Время\'', self)
        self.chkNeedPerson   = QtGui.QCheckBox(u'Печатать \'Ответственный\'', self)
        self.chkNeedMKB      = QtGui.QCheckBox(u'Печатать \'МКБ\'', self)

        self.vLayout.addWidget(self.chkNeedAmountAndUnit)
        self.vLayout.addWidget(self.chkNeedStatus)
        self.vLayout.addWidget(self.chkNeedDatetime)
        self.vLayout.addWidget(self.chkNeedPerson)
        self.vLayout.addWidget(self.chkNeedMKB)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        self.setWindowTitle(u'Условия формирования отчета \'Лабораторный журнал\'')
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)

    def setEnabledOrderBy(self, value):
        self.cmbOrderBy.setEnabled(value)

    def orderBy(self):
        return self.cmbOrderBy.currentIndex()

    def getItem(self):
        ok = self.exec_()

        result = smartDict()
        result.clientIdType = self.cmbIdentifierTypes.currentText()
        result.needAmountAndUnit = self.chkNeedAmountAndUnit.isChecked()
        result.chkNeedStatus = self.chkNeedStatus.isChecked()
        result.chkNeedDatetime = self.chkNeedDatetime.isChecked()
        result.chkNeedPerson = self.chkNeedPerson.isChecked()
        result.chkNeedMKB = self.chkNeedMKB.isChecked()
        result.orderBy = self.orderBy()

        return result, ok

    def setClientIdentifierTypesList(self, clientIdentifierTypesList):
        self.cmbIdentifierTypes.clear()
        self.cmbIdentifierTypes.addItems(clientIdentifierTypesList)

    def setPreviousSelectedClientIdentifier(self, previousSelectedClientIdentifier):
        self.cmbIdentifierTypes.setCurrentIndex(previousSelectedClientIdentifier)

class CTotalEditorDialog(QtGui.QDialog):
    def __init__(self, parent, subEditor):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Редактор общего значения')
        self.subEditor = subEditor
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.addWidget(self.subEditor)
        self._isNullValue = False
        self.chkSetNull = QtGui.QCheckBox(u'Очистить', self)
        self.vLayout.addWidget(self.chkSetNull)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)
        self.connect(self.chkSetNull, QtCore.SIGNAL('clicked(bool)'), self.on_chkSetNull_clicked)

    def on_chkSetNull_clicked(self, value):
        self.subEditor.setEnabled(not value)
        self._isNullValue = value

    def isNullValue(self):
        return self._isNullValue

    def editor(self):
        return self.subEditor




class CSamplingApplyDialog(CDialogBase):
    def __init__(self, parent, tissueExternalId, equipmentId, testGroupVisible=False, autoEquipment=False):
        CDialogBase.__init__(self, parent)
        self.vLayout = QtGui.QVBoxLayout()
        self.lblExternalId = QtGui.QLabel(u'Идентификатор', self)
        self.vLayout.addWidget(self.lblExternalId)
        self.edtExternalId = QtGui.QLineEdit(tissueExternalId, self)
        self.vLayout.addWidget(self.edtExternalId)
        self.lblEquipment = QtGui.QLabel(u'Оборудование', self)
        self.vLayout.addWidget(self.lblEquipment)

        self.cmbEquipment = CRBComboBox(self)
        specialValues = ((-1, '-', u'Автоопределение оборудования'), ) if autoEquipment else None
        self.cmbEquipment.setTable('rbEquipment', addNone=True, specialValues=specialValues)
        self.cmbEquipment.setValue(equipmentId)

        self.vLayout.addWidget(self.cmbEquipment)
        self.lblTestGroup = QtGui.QLabel(u'Группа тестов', self)
        self.vLayout.addWidget(self.lblTestGroup)
        self.cmbTestGroup = CRBComboBox(self)
        self.cmbTestGroup.setTable('rbTestGroup', addNone=True)
        self.vLayout.addWidget(self.cmbTestGroup)

        self.lblExternalId.setVisible(not testGroupVisible)
        self.edtExternalId.setVisible(not testGroupVisible)

        self.lblTestGroup.setVisible(testGroupVisible)
        self.cmbTestGroup.setVisible(testGroupVisible)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)

        self._tissueJournalId = None
        self._tissueTypeId    = None
        self._datetimeTaken   = None


        self.setWindowTitle(u'Регистрация проб')

    def setSettings(self, tissueJournalId, tissueTypeId, datetimeTaken):
        self._tissueJournalId = tissueJournalId
        self._tissueTypeId    = tissueTypeId
        self._datetimeTaken   = datetimeTaken

    def checkDataEntered(self):
        result = True
        result = result and self.checkExternalId()
        return result

    def saveData(self):
        return self.checkDataEntered()

    def checkExternalId(self):
        result = True

        if self.edtExternalId.isVisible():
            message = u''
            externalId = forceStringEx(self.edtExternalId.text())
            if bool(externalId):
                if not externalId.isdigit():
                    result = False
                    message = u'корректный идентификатор'
            else:
                result = False
                message = u'идентификатор'

            result = result or self.checkInputMessage(message, False, self.edtExternalId)
            result = result and self.checkSelectedToSave(externalId, self._tissueJournalId)

        return result

    def checkSelectedToSave(self, externalId, tissueJournalId):
        db = QtGui.qApp.db
        tableProbe = db.table('Probe')
        tableTissueJournal = db.table('TakenTissueJournal')

        cond = [tableProbe['takenTissueJournal_id'].ne(tissueJournalId),
                tableProbe['externalId'].eq(externalId),
                tableTissueJournal['tissueType_id'].eq(self._tissueTypeId),
                tableTissueJournal['deleted'].eq(0)]

        dateCond = getExternalIdDateCond(self._tissueTypeId, self._datetimeTaken)

        if dateCond:
            cond.append(dateCond)

        queryTable = tableProbe.innerJoin(tableTissueJournal,
                                          tableTissueJournal['id'].eq(tableProbe['takenTissueJournal_id']))

        record = QtGui.qApp.db.getRecordEx(queryTable, tableProbe['id'].name(), cond)
        if record and forceRef(record.value('id')):
            return self.checkInputMessage(u'другой идентификатор.\nТакой уже существует', False, self.edtExternalId)
        return True

    def externalId(self):
        result = forceStringEx(self.edtExternalId.text()).lstrip('0')
        return (6-len(result))*'0'+result


    def equipmentId(self):
        return self.cmbEquipment.value()

    def testGroupId(self):
        return self.cmbTestGroup.value()

# ###############################################################

class CTissueJournalTotalEditorDialog(QtGui.QDialog, Ui_TissueJournalTotalEditorDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setVisibleMKBWidgets(False)
        self.isVisibleExtraAssistants = False
        self.setVisibleExtraAssistants(self.isVisibleExtraAssistants)
        self.valuesDict = {'personIdInJournal':None,
                           'personIdInAction':None,
                           'assistantIdInAction':None,
                           'assistantIdInAction2':None,
                           'assistantIdInAction3':None,
                           'status':None,
                           'mkb': None,
                           'morphologyMKB': None}


    def exec_(self):
        self.chkStatus.setFocus(QtCore.Qt.OtherFocusReason)
        return QtGui.QDialog.exec_(self)

    def setStatusNames(self, statuses):
        for i in range(self.cmbStatus.count()):
            self.cmbStatus.removeItem(0)
        if QtGui.qApp.defaultKLADR().startswith('23'):
            self.cmbStatus.addItems(statuses)
        else:
            self.cmbStatus.addItems(statuses[:7])

    def values(self):
        if self.chkPersonInJournal.isChecked():
            self.valuesDict['personIdInJournal'] = self.cmbPersonInJournal.value()
        if self.chkPersonInAction.isChecked():
            self.valuesDict['personIdInAction'] = self.cmbPersonInAction.value()
        if self.chkAssistantInAction.isChecked():
            self.valuesDict['assistantIdInAction'] = self.cmbAssistantInAction.value()
            if self.isVisibleExtraAssistants: #atronah: doesn't use
                self.valuesDict['assistantIdInAction2'] = self.cmbAssistantInAction2.value()
                self.valuesDict['assistantIdInAction3'] = self.cmbAssistantInAction3.value()
        if self.chkStatus.isChecked():
            self.valuesDict['status'] = self.cmbStatus.currentIndex()
        if self.chkMKB.isChecked():
            self.valuesDict['mkb'] = self.cmbMKB.text()
        if self.chkMorphologyMKB.isChecked():
            self.valuesDict['morphologyMKB'] = self.cmbMorphologyMKB.validText()
        return self.valuesDict

    def setVisibleExtraAssistants(self, value):
        self.isVisibleExtraAssistants = value
        #self.cmbAssistantInAction2.setVisible(value)
        #self.cmbAssistantInAction3.setVisible(value)
        #self.cmbAssistantInAction2.setEnabled(value)
        #self.cmbAssistantInAction3.setEnabled(value)
        if value:
            self.chkAssistantInAction.setText(u'Ассистенты в действии')
        else:
            self.chkAssistantInAction.setText(u'Ассистент в действии')

    def setPersonInJournal(self, value):
        self.cmbPersonInJournal.setValue(value)


    def setPersonIdInAction(self, value):
        self.cmbPersonInAction.setValue(value)


    def setAssistantInAction(self, value):
        self.cmbAssistantInAction.setValue(value)


    def setAssistantInAction2(self, value):
        self.cmbAssistantInAction2.setValue(value)


    def setAssistantInAction3(self, value):
        self.cmbAssistantInAction3.setValue(value)

    def setStatus(self, value):
        self.cmbStatus.setCurrentIndex(value)


    def setMKB(self, mkb):
        self.cmbMKB.setText(mkb)


    def setMorphology(self, morphology):
        self.cmbMorphologyMKB.setText(morphology)


    def updateIsChecked(self, value = False):
        self.chkPersonInJournal.setChecked(value)
        self.chkPersonInAction.setChecked(value)
        self.chkAssistantInAction.setChecked(value)
        self.chkStatus.setChecked(value)
        self.chkMKB.setChecked(value)
        self.chkMorphologyMKB.setChecked(value)


    def setVisibleMKBWidgets(self, value):
        for widget in [self.chkMKB, self.chkMorphologyMKB,
                       self.cmbMKB, self.cmbMorphologyMKB]:
            widget.setVisible(value)

    def setVisibleJournalWidgets(self, value):
        self.chkPersonInJournal.setVisible(value)
        self.cmbPersonInJournal.setVisible(value)
        mkbWidgetsVisible = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self.setVisibleMKBWidgets(mkbWidgetsVisible)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbMKB_textChanged(self, value):
        if value[-1:] == '.':
            value = value[:-1]
        diagName = forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', value, 'DiagName'))
        if diagName:
            self.lblMKBText.setText(diagName)
        else:
            self.lblMKBText.clear()
#        self.cmbMorphologyMKB.setMKBFilter(self.cmbAPMorphologyMKB.getMKBFilter(unicode(value)))


    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbMorphologyMKB_textChanged(self, value):
        if self.cmbMorphologyMKB.isValid(value):
            name = forceString(QtGui.qApp.db.translate('MKB_Morphology', 'code', value, 'name'))
            if name:
                self.lblMorphologyMKBText.setText(name)
            else:
                self.lblMorphologyMKBText.clear()
        else:
            self.lblMorphologyMKBText.clear()


# #############

class CEmptyEditor(QtGui.QWidget):
    def value(self):
        return QtCore.QVariant()

    def setValue(self, value):
        pass

# ############

class CInfoListHelper(list):
    def append(self, key, value):
        list.append(self, '<P><B>%s:</B> %s</P>'%(key, value))

# #############################################################

def getActionContextListByTissue(tissueJournalId):
    db = QtGui.qApp.db
    tableTissueJournal = db.table('TakenTissueJournal')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    queryTable = tableTissueJournal.innerJoin(tableAction,
                                              tableAction['takenTissueJournal_id'].eq(tableTissueJournal['id']))
    queryTable = queryTable.innerJoin(tableActionType,
                                      tableActionType['id'].eq(tableAction['actionType_id']))
    cond = tableTissueJournal['id'].eq(tissueJournalId)
    field = tableActionType['context'].name()

    stmt = db.selectStmt(queryTable, field, cond, isDistinct = True)
    query = db.query(stmt)
    result = []
    while query.next():
        context = forceString(query.value(0))
        result.append(context)
    return result

def getDependentEventIdList(tissueJournalId):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableEvent  = db.table('Event')
    queryTable = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
    cond = [tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableAction['takenTissueJournal_id'].eq(tissueJournalId)]
    return db.getDistinctIdList(queryTable, tableEvent['id'].name(), cond)


def deleteEventsIfWithoutActions(eventIdList):
    for eventId in eventIdList:
        db = QtGui.qApp.db
        tableEvent  = db.table('Event')
        tableAction = db.table('Action')
        cond = [tableAction['deleted'].eq(0), tableEvent['id'].eq(eventId)]
        queryTable = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
        actionIdList = db.getDistinctIdList(queryTable, tableAction['id'].name(), cond)
        if not len(actionIdList) > 0:
            diagnosisIdList = db.getIdList('Diagnostic', idCol='diagnosis_id', where='event_id=%d'%eventId)
            db.deleteRecord(tableEvent, tableEvent['id'].eq(eventId))
            if diagnosisIdList:
                tableDiagnosis = db.table('Diagnosis')
                diagnosisDeleteCond = [
                            tableDiagnosis['id'].inlist(diagnosisIdList),
                            'NOT EXISTS (SELECT * FROM Diagnostic WHERE Diagnostic.diagnosis_id = Diagnosis.id)',
                            'NOT EXISTS (SELECT * FROM TempInvalid WHERE TempInvalid.diagnosis_id = Diagnosis.id)'
                                      ]
                db.deleteRecord(tableDiagnosis, diagnosisDeleteCond)

def checkActionPreliminaryResultByTissueJournalIdList(tissueJournalIdList):
    db = QtGui.qApp.db

    tableProbe              = db.table('Probe')
    tableAction             = db.table('Action')
    tableActionType         = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')

    queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionPropertyType,
                                        tableActionPropertyType['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableProbe,
                                        [tableProbe['takenTissueJournal_id'].eq(tableAction['takenTissueJournal_id']),
                                        tableProbe['test_id'].eq(tableActionPropertyType['test_id'])])

    allActionIdList = db.getDistinctIdList(tableAction, 'id',
                                            tableAction['takenTissueJournal_id'].inlist(tissueJournalIdList))
    okActionIdList = db.getDistinctIdList(queryTable, tableAction['id'].name(), tableAction['id'].inlist(allActionIdList))

    templateStmt = 'UPDATE `Action` SET preliminaryResult=0 WHERE id=%(actionId)d'
    for actionId in (set(allActionIdList) - set(okActionIdList)):
        db.query(templateStmt % {'actionId':actionId})


def setProbeResultToActionProperties(tissueJournalId, testId, result):
    db = QtGui.qApp.db

    tableAction = db.table('Action')
    tableActionPropertyType = db.table('ActionPropertyType')

    queryTable = tableAction.innerJoin(tableActionPropertyType,
                                        tableActionPropertyType['actionType_id'].eq(tableAction['actionType_id']))

    cond = [tableAction['takenTissueJournal_id'].eq(tissueJournalId),
            tableActionPropertyType['test_id'].eq(testId)]

    actionRecordList = db.getRecordList(queryTable, 'Action.*', cond)

    for actionRecord in actionRecordList:

        needSave = False

        action = CAction(record=actionRecord)

        actionType = action.getType()
        propertyTypeItemsList = actionType.getPropertiesById().items()
        for propertyTypeId, propertyType in propertyTypeItemsList:
            if propertyType.testId == testId:
                property = action.getPropertyById(propertyTypeId)
                if not propertyType.isVector:
                    property.setValue(propertyType.convertQVariantToPyValue(result))
                    needSave = True

        if needSave:
            action.save(idx=forceInt(actionRecord.value('idx')))

# ################################

def setActionPreliminaryResult(mapActionId2PreliminaryResult):
    db = QtGui.qApp.db
    templateStmt = 'UPDATE `Action` SET preliminaryResult=%(result)d WHERE id=%(actionId)d'
    for actionId in mapActionId2PreliminaryResult.keys():
        preliminaryResultList = mapActionId2PreliminaryResult.get(actionId)
        existsResult = len(filter(lambda x: x==probeIsFinished,
                                    preliminaryResultList[1:])) > 0

        if existsResult:
            QtGui.qApp.db.query(templateStmt%{'result':1, 'actionId':actionId})
        else:
            QtGui.qApp.db.query(templateStmt%{'result':2, 'actionId':actionId})

def computeActionPreliminaryResult(probeItem, mapActionId2PreliminaryResult):
    testId = forceRef(probeItem.value('test_id'))
    tissueJournalId = forceRef(probeItem.value('takenTissueJournal_id'))

    db = QtGui.qApp.db
    tableTissueJournal      = db.table('TakenTissueJournal')
    tableAction             = db.table('Action')
    tableActionType         = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')

    queryTable = tableAction.innerJoin(tableTissueJournal,
                                        tableTissueJournal['id'].eq(tableAction['takenTissueJournal_id']))
    queryTable = queryTable.innerJoin(tableActionType,
                                        tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionPropertyType,
                                        tableActionPropertyType['actionType_id'].eq(tableActionType['id']))

    cond = [tableTissueJournal['id'].eq(tissueJournalId),
            tableActionPropertyType['test_id'].eq(testId)]

    recordList = db.getRecordList(queryTable, 'Action.*', cond)

    for record in recordList:
        actionId = forceRef(record.value('id'))
        preliminaryResult = forceInt(record.value('preliminaryResult'))
        if preliminaryResult != 1:
            preliminaryResultList = mapActionId2PreliminaryResult.setdefault(actionId, [preliminaryResult])
            preliminaryResultList.append(forceInt(probeItem.value('status')))


# ##########################################################
class CTissueJournalActionTypeStack():
    cacheActionTypeTestIdList = {}

    def __init__(self, tissueJournalId):
        db = QtGui.qApp.db
        self.actionTypeIdList = db.getIdList('Action',
                                             'actionType_id',
                                             'takenTissueJournal_id=%d'%tissueJournalId)

        for actionTypeId in self.actionTypeIdList:
            if not actionTypeId in CTissueJournalActionTypeStack.cacheActionTypeTestIdList.keys():
                result = db.getDistinctIdList('ActionPropertyType',
                                              'test_id',
                                              'actionType_id=%d'%actionTypeId)
                CTissueJournalActionTypeStack.cacheActionTypeTestIdList[actionTypeId] = result
        self.testIdPosition = {}
        self.count = len(self.actionTypeIdList)

    def next(self, testId):
        position = self.testIdPosition.setdefault(testId, 0)
        while position < self.count:
            if testId in CTissueJournalActionTypeStack.cacheActionTypeTestIdList[self.actionTypeIdList[position]]:
                return self.actionTypeIdList[position]
            else:
                position += 1
                self.testIdPosition[testId] = position
        return None

class CTissueJournalActionTypeHelper():
    cache = {}

    @classmethod
    def reset(cls):
        cls.cache.clear()
        CTissueJournalActionTypeStack.cacheActionTypeTestIdList.clear()

    @classmethod
    def next(cls, tissueJournalId, testId):
        stack = cls.cache.get(tissueJournalId, None)
        if not stack:
            stack = CTissueJournalActionTypeStack(tissueJournalId)
            cls.cache[tissueJournalId] = stack
        return stack.next(testId)

def getNextTissueJournalActionType(tissueJournalId, testId):
    return CTissueJournalActionTypeHelper.next(tissueJournalId, testId)

def resetTissueJournalActionTypeStackHelper():
    CTissueJournalActionTypeHelper.reset()

class CContainerTypeCache():
    cache = {}

    @classmethod
    def reset(cls):
        cls.cache.clear()

    @classmethod
    def get(cls, actionTypeId, tissueTypeId):
        key = (actionTypeId, tissueTypeId)
        result = cls.cache.get(key, None)
        if not result:
            db = QtGui.qApp.db

            table = db.table('ActionType_TissueType')
            cond = [table['master_id'].eq(actionTypeId),
                    table['tissueType_id'].eq(tissueTypeId)]
            record = db.getRecordEx(table, 'containerType_id, amount', cond)
            if record:
                containerTypeId = forceRef(record.value('containerType_id'))
                containerRecord = db.getRecord('rbContainerType', '*', containerTypeId)
                if containerRecord:
                    container       = ' | '.join([forceString(containerRecord.value('code')),
                                                  forceString(containerRecord.value('name'))
                                                 ]
                                                )
                    color           = forceString(containerRecord.value('color'))
                    tissueAmount    = forceDouble(record.value('amount'))
                    containerCapacity = forceDouble(containerRecord.value('amount'))

                    result = ([None, container, QtGui.QColor(color), tissueAmount, tissueAmount, containerCapacity],
                              containerTypeId)
                else:
                    result = (None, containerTypeId)
            else:
                result = (None, None)

            cls.cache[key] = result

        return result

def getContainerTypeValues(actionTypeId, tissueTypeId):
    return CContainerTypeCache.get(actionTypeId, tissueTypeId)

def resetContainerTypeCache():
    CContainerTypeCache.reset()

# ##########################################################


class CSamplePreparationProgressBar(CProgressBar):
    def __init__(self, itemsCount=0, parent=None):
        CProgressBar.__init__(self, parent)
        self.setMaximum(itemsCount)




if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    w = CSamplePreparationProgressBar(10)
    w.show()
    app.exec_()




