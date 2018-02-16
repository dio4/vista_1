# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import re
import sip

from PyQt4 import QtCore, QtGui

from DataCheck.LocalLogicalControlDiagnosisLUD import CLocalLogicalControlDiagnosisLUD

from Events.Utils                   import getMKBName

from library.DialogBase             import CConstructHelperMixin
from library.DockWidget             import CDockWidget
from library.PreferencesMixin       import CPreferencesMixin, CContainerPreferencesMixin
from library.Utils                  import forceBool, forceDate, forceInt, forceRef, forceString, toVariant, \
                                           formatBool, getPref, setPref

from Registry.ChangeMKBEditDialog   import CChangeMKBEditDialog

from Users.Rights                   import urChangeDiagnosis, urChangeMKB, urLocalControlLUD, urRegWriteInsurOfficeMark

from Ui_DignosisDockContent         import Ui_Form


class CDiagnosisDockWidget(CDockWidget):
    def __init__(self, parent):
        CDockWidget.__init__(self, parent)
        self.setWindowTitle(u'ЛУД')
        self.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.content = None
        self.contentPreferences = {}
        self.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), self.onConnectionChanged)


    def loadPreferences(self, preferences):
        self.contentPreferences = getPref(preferences, 'content', {})
        CDockWidget.loadPreferences(self, preferences)
        if isinstance(self.content, CPreferencesMixin):
            self.content.loadPreferences(self.contentPreferences)


    def savePreferences(self):
        result = CDockWidget.savePreferences(self)
        self.updateContentPreferences()
        setPref(result,'content',self.contentPreferences)
        return result


    def updateContentPreferences(self):
        if isinstance(self.content, CPreferencesMixin):
            self.contentPreferences = self.content.savePreferences()


    def onConnectionChanged(self, value):
        if value:
            self.onDBConnected()
        else:
            self.onDBDisconnected()


    def onDBConnected(self):
        self.setWidget(None)
        if self.content:
            self.content.setParent(None)
            sip.delete(self.content)
        self.content = CDiagnosisDockContent(self)
        self.content.loadPreferences(self.contentPreferences)
        self.setWidget(self.content)


    def onDBDisconnected(self):
        self.setWidget(None)
        if self.content:
            self.updateContentPreferences()
            self.content.setParent(None)
            sip.delete(self.content)
        self.content = QtGui.QLabel(u'необходимо\nподключение\nк базе данных', self)
        self.content.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.content.setDisabled(True)
        self.setWidget(self.content)



class CDiagnosisDockContent(QtGui.QWidget, Ui_Form, CConstructHelperMixin, CContainerPreferencesMixin):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        db = QtGui.qApp.db
        self.dtidBase = forceRef(db.translate('rbDiagnosisType', 'code', '2', 'id'))
        self.dtidAcomp = forceRef(db.translate('rbDiagnosisType', 'code', '9', 'id'))
        self.dtidModified = forceRef(db.translate('rbDiagnosisType', 'code', '99', 'id'))

        self.dcidAcute = forceRef(db.translate('rbDiseaseCharacter', 'code', '1', 'id'))
        self.dcidChronical = forceRef(db.translate('rbDiseaseCharacter', 'code', '3', 'id'))

        self.addModels('Chronical', CChronicalModel(self, self.dcidChronical))
        self.addModels('Acute', CAcuteModel(self, self.dcidAcute))
        self.addModels('Factor', CFactorModel(self))
        self.addModels('TempInvalid', CTempInvalidModel(self, 0))
        self.addModels('Disability', CDisabilityModel(self, 1))
        self.addModels('VitalRestriction', CDisabilityModel(self, 2))
        self.addModels('AllergyBox', CAllergyBoxModel(self))
        self.addModels('IntoleranceMedicamentBox', CIntoleranceMedicamentBoxModel(self))
#
        self.actChronicalChangeMKB =  QtGui.QAction(u'Исправить шифр МКБ', self)
        self.actChronicalChangeMKB.setObjectName('actChronicalChangeMKB')
        self.actCronicalShowEvents =  QtGui.QAction(u'Показать обращения', self)
        self.actCronicalShowEvents.setObjectName('actCronicalShowEvents')
        self.actCronicalChangeDiagnosis = QtGui.QAction(u'Изменить диагноз', self)
        self.actCronicalChangeDiagnosis.setObjectName('actCronicalChangeDiagnosis')
        self.actChronicalLocalControlLUD =  QtGui.QAction(u'Контроль ЛУД', self)
        self.actChronicalLocalControlLUD.setObjectName('actChronicalLocalControlLUD')
        self.actAcuteChangeMKB = QtGui.QAction(u'Исправить шифр МКБ', self)
        self.actAcuteChangeMKB.setObjectName('actAcuteChangeMKB')
        self.actAcuteShowEvents = QtGui.QAction(u'Показать обращения', self)
        self.actAcuteShowEvents.setObjectName('actAcuteShowEvents')
        self.actAcuteChangeDiagnosis = QtGui.QAction(u'Изменить диагноз', self)
        self.actAcuteChangeDiagnosis.setObjectName('actAcuteChangeDiagnosis')
        self.actAcuteLocalControlLUD =  QtGui.QAction(u'Контроль ЛУД', self)
        self.actAcuteLocalControlLUD.setObjectName('actAcuteLocalControlLUD')
        self.actTempInvalidFind =     QtGui.QAction(u'Найти документ', self)
        self.actTempInvalidFind.setObjectName('actTempInvalidFind')
        self.actTempInvalidDelete =   QtGui.QAction(u'Удалить документ', self)
        self.actTempInvalidDelete.setObjectName('actTempInvalidDelete')

#
#        self.timer = QTimer(self)
#        self.timer.setObjectName('timer')
#        self.timer.setInterval(60*1000) # раз в минуту

        self.setupUi(self)
        self.setModels(self.tblChronical,   self.modelChronical,   self.selectionModelChronical)
        self.setModels(self.tblAcute,       self.modelAcute,       self.selectionModelAcute)
        self.setModels(self.tblFactor,      self.modelFactor,      self.selectionModelFactor)
        self.setModels(self.tblTempInvalid, self.modelTempInvalid, self.selectionModelTempInvalid)
        self.setModels(self.tblDisability,  self.modelDisability,  self.selectionModelDisability)
        self.setModels(self.tblVitalRestriction,  self.modelVitalRestriction,  self.selectionModelVitalRestriction)
        self.setModels(self.tblAllergyBox,  self.modelAllergyBox,  self.selectionModelAllergyBox)
        self.setModels(self.tblIntoleranceMedicamentBox,  self.modelIntoleranceMedicamentBox,  self.selectionModelIntoleranceMedicamentBox)

        self.cmbFactorFilterSpeciality.setTable('rbSpeciality', order='name')
        self.cmbFactorFilterMKB.setTable('vrbMKBZ', order='code')
        self.cmbFactorFilterSpeciality.setValue(0)
        self.cmbFactorFilterMKB.setValue(0)
        self.filterFactorSpeciality = None
        self.filterFactorMKB = None
        self.tblChronical.createPopupMenu([self.actChronicalChangeMKB, self.actCronicalShowEvents, self.actCronicalChangeDiagnosis, self.actChronicalLocalControlLUD])
        self.tblAcute.createPopupMenu([self.actAcuteChangeMKB, self.actAcuteShowEvents, self.actAcuteChangeDiagnosis, self.actAcuteLocalControlLUD])
        self.tblTempInvalid.createPopupMenu([self.actTempInvalidFind, '-', self.actTempInvalidDelete])
        self.connect(self.tblChronical.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuTblChronicalAboutToShow)
        self.connect(self.tblAcute.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuTblAcuteAboutToShow)
        self.connect(self.tblTempInvalid.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuTblTempInvalidAboutToShow)
#        self.timer.start()
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentClientIdChanged()'), self.updateTables)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentClientInfoChanged()'), self.updateTables)


    def sizeHint(self):
        return QtCore.QSize(10, 10)


    def updateTables(self):
        self.clientId = QtGui.qApp.currentClientId()
        self.updateTablesDiagnosis()
        self.updateTablesFactor()
        self.modelTempInvalid.loadData(self.clientId)
        self.modelDisability.loadData(self.clientId)
        self.modelVitalRestriction.loadData(self.clientId)
        self.updateBloodType(self.clientId)
        self.modelAllergyBox.loadData(self.clientId)
        self.modelIntoleranceMedicamentBox.loadData(self.clientId)


    def updateTablesDiagnosis(self):
        showAccomp   = self.chkShowAccomp.isChecked()
        showModified = self.chkShowModified.isChecked()
        self.modelChronical.loadData(self.clientId, showAccomp, showModified)
        self.modelAcute.loadData(self.clientId, showAccomp, showModified)


    def updateTablesFactor(self):
        self.modelFactor.loadData(self.clientId,  self.filterFactorSpeciality, self.filterFactorMKB, self.cmbFactorFilterMKB.code())


    def updateBloodType(self, clientId):
        if clientId:
            db = QtGui.qApp.db
            tableClient = db.table('Client')
            tableBloodType = db.table('rbBloodType')
            queryTable = tableClient.leftJoin(tableBloodType, tableBloodType['id'].eq(tableClient['bloodType_id']))
            records = db.getRecordList(queryTable, tableBloodType['name'].name(), tableClient['id'].eq(clientId))
        else:
            records = []
        bloodTypeName = forceString(records[0].value('name')) if records else ''
        self.lblBloodTypeBox.setText(bloodTypeName if bloodTypeName else u'не указано')


    def changeMKB(self, diagnosisId):
        if diagnosisId:
            dialog = CChangeMKBEditDialog(self)
            dialog.load(diagnosisId)
            if dialog.exec_():
                self.updateTables()


    def setEventFilterByDiagnosis(self, diagnosisId):
        if diagnosisId:
            db = QtGui.qApp.db
            tableDiagnosis = db.table('Diagnosis')
            tableDiagnostic = db.table('Diagnostic')
            tableEvent = db.table('Event')
            queryTable = tableDiagnosis.leftJoin(tableDiagnostic, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
            queryTable = queryTable.leftJoin(tableEvent, tableDiagnostic['event_id'].eq(tableEvent['id']))
            eventIdList = db.getDistinctIdList(queryTable,  tableEvent['id'].name(), tableDiagnosis['id'].eq(diagnosisId), ['Event.execDate DESC', 'Event.id'])
            QtGui.qApp.setEventList(eventIdList)


    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbFactorFilterSpeciality_currentIndexChanged (self):
        self.filterFactorSpeciality = self.cmbFactorFilterSpeciality.value()
        self.clientId = QtGui.qApp.currentClientId()
        if self.clientId:
            self.modelFactor.loadData(self.clientId, self.filterFactorSpeciality, self.filterFactorMKB)


    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbFactorFilterMKB_currentIndexChanged (self):
        self.filterFactorMKB = self.cmbFactorFilterMKB.value()
        self.clientId = QtGui.qApp.currentClientId()
        if self.clientId:
            self.modelFactor.loadData(self.clientId, self.filterFactorSpeciality, self.filterFactorMKB, self.cmbFactorFilterMKB.code())


    @QtCore.pyqtSlot(bool)
    def on_chkShowAccomp_toggled(self, checked):
        self.updateTablesDiagnosis()


    @QtCore.pyqtSlot(bool)
    def on_chkShowModified_toggled(self, checked):
        self.updateTablesDiagnosis()


    def popupMenuTblChronicalAboutToShow(self):
        row = self.tblChronical.currentIndex().row()
        self.actChronicalChangeMKB.setEnabled(row>=0 and QtGui.qApp.userHasRight(urChangeMKB))
        self.actCronicalShowEvents.setEnabled(row>=0 and QtGui.qApp.canFindEvent())
        self.actCronicalChangeDiagnosis.setEnabled(row>=0 and QtGui.qApp.userHasRight(urChangeDiagnosis) and False)
        self.actChronicalLocalControlLUD.setEnabled(row>=0 and QtGui.qApp.userHasRight(urLocalControlLUD))


    def popupMenuTblAcuteAboutToShow(self):
        row = self.tblAcute.currentIndex().row()
        self.actAcuteChangeMKB.setEnabled(row>=0 and QtGui.qApp.userHasRight(urChangeMKB))
        self.actAcuteShowEvents.setEnabled(row>=0 and QtGui.qApp.canFindEvent())
        self.actAcuteChangeDiagnosis.setEnabled(row>=0 and QtGui.qApp.userHasRight(urChangeDiagnosis) and False)
        self.actAcuteLocalControlLUD.setEnabled(row>=0 and QtGui.qApp.userHasRight(urLocalControlLUD))


    def popupMenuTblTempInvalidAboutToShow(self):
        row = self.tblTempInvalid.currentIndex().row()
        self.actTempInvalidFind.setEnabled(row>=0 and QtGui.qApp.canFindEvent())
        self.actTempInvalidDelete.setEnabled(row>=0)


    @QtCore.pyqtSlot()
    def on_actChronicalChangeMKB_triggered(self):
        row = self.tblChronical.currentIndex().row()
        diagnosisId = self.modelChronical.getDiagnosisId(row)
        self.changeMKB(diagnosisId)


    @QtCore.pyqtSlot()
    def on_actChronicalLocalControlLUD_triggered(self):
        row = self.tblChronical.currentIndex().row()
        CLocalLogicalControlDiagnosisLUD(self, True, False).exec_()


    @QtCore.pyqtSlot()
    def on_actCronicalShowEvents_triggered(self):
        row = self.tblChronical.currentIndex().row()
        diagnosisId = self.modelChronical.getDiagnosisId(row)
        self.setEventFilterByDiagnosis(diagnosisId)


    @QtCore.pyqtSlot()
    def on_actCronicalChangeDiagnosis_triggered(self):
        pass


    @QtCore.pyqtSlot()
    def on_actAcuteChangeMKB_triggered(self):
        row = self.tblAcute.currentIndex().row()
        diagnosisId = self.modelAcute.getDiagnosisId(row)
        self.changeMKB(diagnosisId)


    @QtCore.pyqtSlot()
    def on_actAcuteLocalControlLUD_triggered(self):
        row = self.tblAcute.currentIndex().row()
        CLocalLogicalControlDiagnosisLUD(self, False, True).exec_()


    @QtCore.pyqtSlot()
    def on_actAcuteShowEvents_triggered(self):
        row = self.tblAcute.currentIndex().row()
        diagnosisId = self.modelAcute.getDiagnosisId(row)
        self.setEventFilterByDiagnosis(diagnosisId)


    @QtCore.pyqtSlot()
    def on_actAcuteChangeDiagnosis_triggered(self):
        pass


    @QtCore.pyqtSlot()
    def on_actTempInvalidFind_triggered(self):
        row = self.tblTempInvalid.currentIndex().row()
        tempInvalidId = self.modelTempInvalid.getTempInvalidId(row) if row>=0 else None
        if tempInvalidId:
            db = QtGui.qApp.db
            record = db.getRecord('TempInvalid', 'begDate, endDate', tempInvalidId)
            if record:
                begDate = forceDate(record.value('begDate'))
                endDate = forceDate(record.value('endDate'))
                tableEventType = db.table('EventType')
                eventTypeIdList = db.getIdList(tableEventType, 'id', tableEventType['code'].inlist(['01']))
                tableEvent = db.table('Event')
                cond = [tableEvent['execDate'].ge(begDate),
                        tableEvent['execDate'].lt(endDate.addDays(1)),
                        tableEvent['deleted'].eq(0),
                        tableEvent['client_id'].eq(self.clientId),
                        tableEvent['eventType_id'].inlist(eventTypeIdList),
                       ]
                eventRecord = db.getRecordEx(tableEvent, 'id', cond, 'execDate DESC')
                if eventRecord:
                    eventId = forceRef(eventRecord.value('id'))
                    QtGui.qApp.findEvent(eventId)
            self.updateTables()


    @QtCore.pyqtSlot()
    def on_actTempInvalidDelete_triggered(self):
        def _deleteTempInvalid(tempInvalidId):
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            tablePeriod = db.table('TempInvalid_Period')
            tableResult = db.table('rbTempInvalidResult')
#            record = db.getRecord(table, 'id, deleted', tempInvalidId)
#            if record:
#                record.setValue('deleted',  QVariant(True))
#                db.updateRecord(table, record)
#            insuranceOfficeMark = forceInt(db.translate(table, 'id', tempInvalidId, 'insuranceOfficeMark'))
            record = db.getRecordEx(table, [table['insuranceOfficeMark'], table['prev_id']], [table['id'].eq(tempInvalidId), table['deleted'].eq(0)])
            insuranceOfficeMark = 0
            prevId = None
            if record:
                insuranceOfficeMark = forceInt(record.value('insuranceOfficeMark'))
                prevId = forceRef(record.value('prev_id'))
            recordPrev = db.getRecordEx(table, [table['id']], [table['prev_id'].eq(tempInvalidId), table['deleted'].eq(0)])
            prevTempInvalidId = None
            if recordPrev:
                prevTempInvalidId = forceRef(recordPrev.value('id'))
            closedResult = 0
            if prevId:
                queryTable = tablePeriod.innerJoin(table, tablePeriod['master_id'].eq(table['id']))
                queryTable = queryTable.innerJoin(tableResult, tableResult['id'].eq(tablePeriod['result_id']))
                recordClosed = db.getRecordEx(queryTable, [tableResult['closed'].alias('closedResult')], [table['id'].eq(prevId), table['deleted'].eq(0)], 'TempInvalid_Period.endDate DESC')
                if recordClosed:
                    closedResult = forceInt(recordClosed.value('closedResult'))
            if (not prevTempInvalidId) and (not insuranceOfficeMark or (insuranceOfficeMark and QtGui.qApp.userHasRight(urRegWriteInsurOfficeMark))):
                if prevId:
                    db.updateRecords(table.name(), table['closed'].eq(closedResult), [table['id'].eq(prevId), table['deleted'].eq(0)])
                db.deleteRecord(table, table['id'].eq(tempInvalidId))

        row = self.tblTempInvalid.currentIndex().row()
        tempInvalidId = self.modelTempInvalid.getTempInvalidId(row) if row>=0 else None
        if tempInvalidId:
            QtGui.qApp.call(self, _deleteTempInvalid, (tempInvalidId,))
            self.updateTables()

#
# #####################################################################
#

class CChronicalModel(QtCore.QAbstractTableModel):
    headerText = [u'Шифр', u'Установлен', u'Последнее', u'Д.Н.']

    def __init__(self, parent, characterId):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if QtGui.qApp.defaultMorphologyMKBIsVisible():
            self.headerText.insert(1, u'Морф.')
            self.colAdd = 1
        else:
            self.colAdd = 0
        self.characterId = characterId
        self.items = []
        self.limitDate = False
        self.dtidBase = parent.dtidBase
        self.dtidAcomp = parent.dtidAcomp
        self.dtidModified = parent.dtidModified


    def columnCount(self, index = QtCore.QModelIndex()
):
        return len(self.headerText)


    def rowCount(self, index = QtCore.QModelIndex()
):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return QtCore.QVariant(item[column])
        elif role == QtCore.Qt.FontRole:
            item = self.items[row]
            isAccomp = item[6+self.colAdd]
            isModified = item[7+self.colAdd]
            if isAccomp or isModified:
                result = QtGui.QFont()
                if isAccomp:
                    result.setItalic(True)
                if isModified:
                    result.setStrikeOut(True)
                return QtCore.QVariant(result)
        elif role == QtCore.Qt.ToolTipRole:
            if column == 0:
                item = self.items[row]
                if item[8+self.colAdd] is None:
                    MKB = item[4+self.colAdd]
                    MKBEx = item[5+self.colAdd]
                    item[8+self.colAdd] = calcMKBToolTip(MKB, MKBEx)
                return QtCore.QVariant(item[8+self.colAdd])
        return QtCore.QVariant()



    def loadData(self, clientId, showAccomp, showModified):
        self.items = []
        if clientId:
            db = QtGui.qApp.db
            tableDiagnosis = db.table('Diagnosis')
            tableDispanser = db.table('rbDispanser')
            table = tableDiagnosis.leftJoin(tableDispanser, tableDispanser['id'].eq(tableDiagnosis['dispanser_id']))
            cols = [tableDiagnosis['id'],
                    tableDiagnosis['MKB'],
                    tableDiagnosis['MKBEx'],
                    tableDiagnosis['morphologyMKB'],
                    tableDiagnosis['setDate'],
                    tableDiagnosis['endDate'],
                    tableDispanser['observed'],
                    tableDiagnosis['mod_id'],
                    tableDiagnosis['diagnosisType_id'],
                    tableDiagnosis['character_id']
                    ]
            cond = [tableDiagnosis['client_id'].eq(clientId),
                    tableDiagnosis['character_id'].eq(self.characterId),
                    tableDiagnosis['deleted'].eq(0)]
            dtIdList = [self.dtidBase]
            if showAccomp:
                dtIdList.append(self.dtidAcomp)
            if showModified:
                dtIdList.append(self.dtidModified)
            cond.append(tableDiagnosis['diagnosisType_id'].inlist(dtIdList))
            if not showModified:
                cond.append(tableDiagnosis['mod_id'].isNull())
#            if self.limitDate:
#                cond.append(tableDiagnosis['endDate'].ge(getLimitDate()))

            records = db.getRecordList(table, cols, cond, tableDiagnosis['endDate'].name()+' DESC')
            for record in records:
                id = forceRef(record.value('id'))
                MKB = forceString(record.value('MKB'))
                MKBEx = forceString(record.value('MKBEx'))
                morphologyMKB = forceString(record.value('morphologyMKB'))
                setDate = forceDate(record.value('setDate'))
                endDate = forceDate(record.value('endDate'))
                observed= forceBool(record.value('observed'))
                modId   = forceRef(record.value('mod_id'))
                diagnosisTypeId = forceRef(record.value('diagnosisType_id'))
                characterId = forceRef(record.value('character_id'))
                item = [  (MKB + '+' + MKBEx) if MKBEx else MKB,
                          forceString(setDate),
                          forceString(endDate),
                          formatBool(observed),
                          MKB,
                          MKBEx,
                          diagnosisTypeId != self.dtidBase,
                          bool(modId) or diagnosisTypeId == self.dtidModified,
                          None,
                          id
                       ]
                if self.colAdd:
                    item.insert(1, morphologyMKB)
                self.items.append(item)
        self.reset()


    def getDiagnosisId(self, row):
        return self.items[row][9+self.colAdd] if 0<=row<len(self.items) else None



class CAcuteModel(CChronicalModel):
    headerText = [u'Шифр', u'Начало', u'Окончание', u'Д.Н.']

    def __init__(self, parent, characterId):
        CChronicalModel.__init__(self, parent, characterId)
#        self.limitDate = True
        self.limitDate = False

    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self.headerText)

class CFactorModel(QtCore.QAbstractTableModel):
    headerText = [u'Шифр', u'Дата', u'Врач']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()
):
        return 3


    def rowCount(self, index = QtCore.QModelIndex()
):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return QtCore.QVariant(item[column])
        elif role == QtCore.Qt.ToolTipRole:
            if column == 0:
                item = self.items[row]
                if item[3] is None:
                    MKB = item[0]
                    item[3] = calcMKBToolTip(MKB)
                return QtCore.QVariant(item[3])
        return QtCore.QVariant()


    def loadData(self, clientId, filterSpeciality =  None, filterBlockMKB = None, codeBlockMKB = None):
        self.items = []
        if clientId:
            db = QtGui.qApp.db
            tableDiagnosis = db.table('Diagnosis')
            tablerbSpeciality = db.table('rbSpeciality')
            tabvrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
            cols = [tableDiagnosis['MKB'],
                    tableDiagnosis['setDate'],
                    tabvrbPersonWithSpeciality['name']
                   ]
            table = tableDiagnosis.leftJoin(tabvrbPersonWithSpeciality, tabvrbPersonWithSpeciality['id'].eq(tableDiagnosis['person_id']))
            cond = [tableDiagnosis['client_id'].eq(clientId),
                    tableDiagnosis['character_id'].isNull(),
                    tableDiagnosis['mod_id'].isNull(),
                    tableDiagnosis['deleted'].eq(0)
                    ]
            if filterSpeciality:
               table = table.leftJoin(tablerbSpeciality, tablerbSpeciality['id'].eq(tabvrbPersonWithSpeciality['speciality_id']))
               cond.append(tabvrbPersonWithSpeciality['speciality_id'].eq(filterSpeciality))
            if filterBlockMKB:
                if codeBlockMKB:
                    queryBlockMKB = re.compile(r"""\s*\(\s*([A-Z][0-9.]+)\s*-\s*([A-Z][0-9.]+)\s*\)\s*""",  re.IGNORECASE)
                    resValueBlockMKB = None
                    resValueBlockMKB = re.match(queryBlockMKB,  codeBlockMKB)
                    if resValueBlockMKB:
                        if len(resValueBlockMKB.groups()) == 2:
                            minValueBlockMKB = resValueBlockMKB.group(1)
                            maxValueBlockMKB = resValueBlockMKB.group(2)
                            cond.append(tableDiagnosis['MKB'].ge(minValueBlockMKB))
                            cond.append(tableDiagnosis['MKB'].le(maxValueBlockMKB))
            records = db.getRecordList(table, cols, cond, tableDiagnosis['endDate'].name()+' DESC')
            for record in records:
                MKB = forceString(record.value('MKB'))
                setDate = forceDate(record.value('setDate'))
                namePerson = forceString(record.value('name'))
                item = [  MKB,                                                                     # 0
                          forceString(setDate),                                                    # 1
                          namePerson,                                                              # 2
                          None                                                                     # 3
                       ]
                self.items.append(item)
        self.reset()


def getLimitDate():
    today = QtCore.QDate.currentDate()
    return min([today.addMonths(-1), QtCore.QDate(today.year(), 1, 1)])


class CTempInvalidModel(QtCore.QAbstractTableModel):
    headerText = [u'Шифр', u'Начало', u'Конец', u'Статус']
    closedDict = {0:u'открыт', 1:u'закрыт', 2:u'продлён', 3:u'передан'}

    def __init__(self, parent, type_):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.type_ = type_


    def columnCount(self, index = QtCore.QModelIndex()
):
        return 4


    def rowCount(self, index = QtCore.QModelIndex()
):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        elif role == QtCore.Qt.ToolTipRole:
            if column == 0:
                item = self.items[row]
                if item[7] is None:
                    MKB = item[4]
                    MKBEx = item[5]
                    item[7] = calcMKBToolTip(MKB, MKBEx)
                return QtCore.QVariant(item[7])
        return QtCore.QVariant()


    def loadData(self, clientId):
        self.items = []
        if clientId:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            tableDiagnosis = db.table('Diagnosis')
            cond = [table['deleted'].eq(0), table['client_id'].eq(clientId), table['type'].eq(self.type_)]
            cols = [table['id'], tableDiagnosis['MKB'], tableDiagnosis['MKBEx'], table['begDate'], table['endDate'], table['closed']]
            queryTable = table.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(table['diagnosis_id']))
            for record in db.getRecordList(queryTable, cols, cond, 'endDate DESC'):
                MKB   = forceString(record.value('MKB'))
                MKBEx = forceString(record.value('MKBEx'))
                begDate = forceDate(record.value('begDate'))
                endDate = forceDate(record.value('endDate'))
                closed  = forceInt(record.value('closed'))
                item = [  (MKB + '+' + MKBEx) if MKBEx else MKB,    # 0
                          forceString(begDate),                     # 1
                          forceString(endDate),                     # 2
                          self.closedDict.get(closed, ''),          # 3
                          MKB,                                      # 4
                          MKBEx,                                    # 5
                          forceRef(record.value('id')),             # 6
                          None                                      # 7
                       ]
                self.items.append(item)
        self.reset()


    def getTempInvalidId(self, row):
        return self.items[row][6]


## ######################################################################

class CDisabilityModel(QtCore.QAbstractTableModel):
    headerText = [u'Тип', u'Начало', u'Конец', u'Режим', u'Статус']
    closedDict = {0:u'открыт', 1:u'закрыт', 2:u'продлён', 3:u'передан'}

    def __init__(self, parent, type_):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.type_ = type_


    def columnCount(self, index = QtCore.QModelIndex()
):
        return 4


    def rowCount(self, index = QtCore.QModelIndex()
):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        elif role == QtCore.Qt.ToolTipRole:
            if column == 0:
                item = self.items[row]
                if item[6] is None:
                    codeDocRegime = item[0]
                    docName = item[4]
                    regimeName = item[5]
                    item[6] = codeDocRegime + ': ' + docName + ' - ' + regimeName
                return QtCore.QVariant(item[6])
        return QtCore.QVariant()


    def loadData(self, clientId):
        self.items = []
        if clientId:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            tableInvalidPeriod = db.table('TempInvalid_Period')
            tableInvalidRegime = db.table('rbTempInvalidRegime')
            tableTempInvalidDocument = db.table('rbTempInvalidDocument')
            cond = [table['deleted'].eq(0), table['client_id'].eq(clientId), table['type'].eq(self.type_), table['endDate'].eq(tableInvalidPeriod['endDate'])]
            cols = [table['id'], tableInvalidRegime['code'], tableInvalidRegime['name'], tableTempInvalidDocument['code'].alias('docCode'), tableTempInvalidDocument['name'].alias('docName'), table['begDate'], table['endDate'], table['closed'], table['serial'], table['number']]
            queryTable = tableInvalidPeriod.leftJoin(table, table['id'].eq(tableInvalidPeriod['master_id']))
            queryTable = queryTable.leftJoin(tableInvalidRegime, tableInvalidRegime['id'].eq(tableInvalidPeriod['regime_id']))
            queryTable = queryTable.leftJoin(tableTempInvalidDocument, tableTempInvalidDocument['id'].eq(table['doctype_id']))
            for record in db.getRecordList(queryTable, cols, cond, 'endDate DESC'):
                regimeCode = forceString(record.value('code'))
                regimeName = forceString(record.value('name'))
                docCode = forceString(record.value('docCode'))
                docName =  forceString(record.value('docName'))
                begDate = forceDate(record.value('begDate'))
                endDate = forceDate(record.value('endDate'))
                closed  = forceInt(record.value('closed'))
                item = [  (docCode + ' - ' + regimeCode),            # 0
                          forceString(begDate),                      # 1
                          forceString(endDate),                      # 2
                          self.closedDict.get(closed, ''),           # 3
                          docName,                                   # 4
                          regimeName,                                # 5
                          None                                       # 6
                       ]
                self.items.append(item)
        self.reset()


class CAllergyBoxModel(QtCore.QAbstractTableModel):
    headerText = [u'Наименование вещества', u'Дата установления', u'Степень']
    dataPower = [u'0 - не известно', u'1 - малая', u'2 - средняя', u'3 - высокая', u'4 - строгая']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()
):
        return 3


    def rowCount(self, index = QtCore.QModelIndex()
):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            if column == 2:
                return QtCore.QVariant(self.dataPower[item[column]])
            else:
                return QtCore.QVariant(item[column])
        elif role == QtCore.Qt.ToolTipRole:
            if column == 0:
                item = self.items[row]
                if item[3] is None:
                    nameSubstance = item[0]
                    item[3] = nameSubstance
                return QtCore.QVariant(item[3])

        return QtCore.QVariant()


    def loadData(self, clientId):
        self.items = []
        if clientId:
            db = QtGui.qApp.db
            tableClientAllergy = db.table('ClientAllergy')
            cols = [tableClientAllergy['nameSubstance'],
                    tableClientAllergy['createDate'],
                    tableClientAllergy['power']
                   ]
            cond = [tableClientAllergy['client_id'].eq(clientId)]
            records = db.getRecordList(tableClientAllergy, cols, cond)
            for record in records:
                nameSubstance = forceString(record.value('nameSubstance'))
                createDate = forceDate(record.value('createDate'))
                power = forceInt(record.value('power'))
                item = [  nameSubstance,
                          forceString(createDate),
                          power,
                          None
                       ]
                self.items.append(item)
        self.reset()



class CIntoleranceMedicamentBoxModel(QtCore.QAbstractTableModel):
    headerText = [u'Наименование медикамента', u'Дата установления', u'Степень']
    dataPower = [u'0 - не известно', u'1 - малая', u'2 - средняя', u'3 - высокая', u'4 - строгая']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()
):
        return 3


    def rowCount(self, index = QtCore.QModelIndex()
):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            if column == 2:
                return QtCore.QVariant(self.dataPower[item[column]])
            else:
                return QtCore.QVariant(item[column])
        elif role == QtCore.Qt.ToolTipRole:
            if column == 0:
                item = self.items[row]
                if item[3] is None:
                    nameMedicament = item[0]
                    item[3] = nameMedicament
                return QtCore.QVariant(item[3])

        return QtCore.QVariant()


    def loadData(self, clientId):
        self.items = []
        if clientId:
            db = QtGui.qApp.db
            tableInteleranceMedicament = db.table('ClientIntoleranceMedicament')
            cols = [tableInteleranceMedicament['nameMedicament'],
                    tableInteleranceMedicament['createDate'],
                    tableInteleranceMedicament['power']
                   ]
            cond = [tableInteleranceMedicament['client_id'].eq(clientId)]
            records = db.getRecordList(tableInteleranceMedicament, cols, cond)
            for record in records:
                nameMedicament = forceString(record.value('nameMedicament'))
                createDate = forceDate(record.value('createDate'))
                power = forceInt(record.value('power'))
                item = [  nameMedicament,
                          forceString(createDate),
                          power,
                          None
                       ]
                self.items.append(item)
        self.reset()



def calcMKBToolTip(MKB, MKBEx=''):
    result = []
    if MKB:
        result.append(MKB+': '+getMKBName(MKB))
    if MKBEx:
        result.append(MKBEx+': '+getMKBName(MKBEx))
    return u'\n'.join(result)
