# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Accounting.Utils import CTariff
from Events.Utils import getEventCode
from Registry.Utils import hasSocStatus
from library.AgeSelector import parseAgeSelector, checkExtendedAgeSelector, findExtendedAgeSelectorDist
from library.ComboBox.ComboBoxPopup import CComboBoxPopup
from library.TableModel import getPref, getPrefBool, getPrefInt, setPref, CTextCol
from library.Utils import MKBwithoutSubclassification, forceString, forceRef, forceInt, argMin


class CMESComboBoxPopup(CComboBoxPopup):
    def __init__(self, parent=None):
        CComboBoxPopup.__init__(self, parent, type='MES')
        self._eventProfileId = None
        self._mesNameTemplate = None
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CMESComboBoxPopup', {})
        # self.table.loadPreferences(preferences)
        self.chkOperativeMes.setVisible(False)
        self.chkDuration.setVisible(False)
        self.chkShowAll.setVisible(False)
        self.tableModel.addColumn(CTextCol(u'Описание', ['descr'], 20))
        self.tableModel.addColumn(CTextCol(u'Модель пациента', ['patientModel'], 25))
        self.getCheckBoxes()

    def setValueIfOnly(self):
        idList = self.table.model().idList()
        if len(idList) == 1:
            self._id = idList[0]
            self.emit(QtCore.SIGNAL('ItemSelected(int)'), idList[0])
            self.close()

    def closeEvent(self, event):
        # preferences = self.table.savePreferences()
        # setPref(QtGui.qApp.preferences.windowPrefs, 'CMESComboBoxPopup', preferences)
        self.emit(QtCore.SIGNAL('closed()'))
        QtGui.QFrame.closeEvent(self, event)

    def on_buttonBox_reset(self):
        self.chkSex.setChecked(True)
        self.chkAge.setChecked(True)
        self.chkContract.setChecked(True)
        self.chkEventProfile.setChecked(True)
        self.chkMesCodeTemplate.setChecked(True)
        self.chkMesNameTemplate.setChecked(True)
        self.chkSpeciality.setChecked(True)
        self.cmbMKB.setCurrentIndex(2)
        self.chkOperativeMes.setChecked(False)

    def on_buttonBox_apply(self):
        idList = self.getMesIdList(self.chkSex.isChecked(),
                                   self.chkAge.isChecked(),
                                   self.chkEventProfile.isChecked(),
                                   self.chkMesCodeTemplate.isChecked(),
                                   self.chkMesNameTemplate.isChecked(),
                                   self.chkSpeciality.isChecked(),
                                   self.chkContract.isChecked(),
                                   self.cmbMKB.currentIndex(),
                                   self.chkOperativeMes.isChecked())
        self.setIdList(idList)
        self.setCheckBoxes('MESCBCheckBoxes')

    def setActionTypeIdList(self, idList):
        CComboBoxPopup.setActionTypeIdList(idList)
        self.chkOperativeMes.setVisible(True)

    def getMesIdList(self, useSex, useAge, useProfile, useMesCode, useMesName, useSpeciality, useContract, mkbCond,
                     operativeMes):
        db = QtGui.qApp.db
        tableMES = db.table('mes.MES')
        queryTable = tableMES
        cond = []

        if (useSex and self._clientSex) or (useAge and self._clientAge):
            tableService = db.table('rbService')
            tableServiceProfile = db.table('rbService_Profile')

            queryTable = queryTable.leftJoin(tableService, tableService['code'].eq(tableMES['code']))
            queryTable = queryTable.leftJoin(tableServiceProfile,
                                             [tableServiceProfile['master_id'].eq(tableService['id']),
                                              tableServiceProfile['speciality_id'].eq(self._specialityId)])

            sexCond = db.joinOr([tableServiceProfile['id'].isNull(),
                                 tableServiceProfile['sex'].inlist([self._clientSex, 0])
                                 ])
            if useSex and self._clientSex:
                cond.append(sexCond)

        if self._actionTypeIdList and operativeMes:
            tableMesService = db.table('mes.MES_service')
            tableMrbService = db.table('mes.mrbService')
            tableService = db.table('rbService')
            tableActionType = db.table('ActionType')
            condTable = tableMesService
            condTable = condTable.innerJoin(tableMrbService, tableMesService['service_id'].eq(tableMrbService['id']))
            condTable = condTable.innerJoin(tableService, tableMrbService['code'].eq(tableService['code']))
            condTable = condTable.innerJoin(tableActionType,
                                            tableService['id'].eq(tableActionType['nomenclativeService_id']))
            subCond = [
                tableMesService['master_id'].eq(tableMES['id']),
                tableActionType['id'].inlist(self._actionTypeIdList)]

            if self._checkDate:
                dateStr = self._checkDate.toString(QtCore.Qt.ISODate)
                subCond.append(
                    'IF(mes.MES_service.begDate IS NULL, 1, mes.MES_service.begDate <= DATE(\'%s\'))' % dateStr)
                subCond.append(
                    'IF(mes.MES_service.endDate IS NULL, 1, mes.MES_service.endDate >= DATE(\'%s\'))' % dateStr)
            cond.append(db.existsStmt(condTable, subCond))

        if self._eventProfileId and useProfile:
            tableMESGroup = db.table('mes.mrbMESGroup')
            tableEventProfile = db.table('rbEventProfile')
            queryTable = queryTable.leftJoin(tableMESGroup, tableMESGroup['id'].eq(tableMES['group_id']))
            queryTable = queryTable.leftJoin(tableEventProfile,
                                             tableEventProfile['regionalCode'].eq(tableMESGroup['code']))
            cond.append(tableEventProfile['id'].eq(self._eventProfileId))
        if self._mesCodeTemplate and useMesCode:
            cond.append(tableMES['code'].regexp(self._mesCodeTemplate))
        if self._mesNameTemplate and useMesName:
            cond.append(tableMES['name'].regexp(self._mesNameTemplate))
        if self._specialityId and useSpeciality:
            regionalCode = db.translate('rbSpeciality', 'id', self._specialityId, 'regionalCode')
            tableMESVisit = db.table('mes.MES_visit')
            tableMESSpeciality = db.table('mes.mrbSpeciality')
            tableMESVisitType = db.table('mes.mrbVisitType')
            subTable = tableMESVisit.leftJoin(tableMESVisitType,
                                              tableMESVisitType['id'].eq(tableMESVisit['visitType_id']))
            subTable = subTable.leftJoin(tableMESSpeciality,
                                         tableMESSpeciality['id'].eq(tableMESVisit['speciality_id']))
            subCond = [tableMESVisit['master_id'].eq(tableMES['id']),
                       tableMESSpeciality['regionalCode'].eq(regionalCode)]

            cond.append(db.joinOr([
                db.existsStmt(subTable, subCond),
                'NOT ' + db.existsStmt(tableMESVisit, tableMESVisit['master_id'].eq(tableMES['id']))
            ]))
        if self._contractId and useContract:
            tableContractTariff = db.table('Contract_Tariff')
            tableContractService = db.table('rbService').alias('contractService')
            queryTable = queryTable.leftJoin(tableContractService, tableMES['code'].eq(tableContractService['code']))
            queryTable = queryTable.leftJoin(
                tableContractTariff,
                db.joinAnd([
                    tableContractService['id'].eq(tableContractTariff['service_id']),
                    tableContractTariff['deleted'].eq(0),
                    tableContractTariff['tariffType'].inlist([CTariff.ttVisitsByMES,
                                                              CTariff.ttEventByMES,
                                                              CTariff.ttEventByMESLen,
                                                              CTariff.ttActionsByMES])
                ])
            )
            cond.append(tableContractTariff['master_id'].eq(self._contractId))
            if self._endDateForTariff:
                cond.append(db.joinOr([tableContractTariff['begDate'].dateLe(self._endDateForTariff),
                                       tableContractTariff['begDate'].isNull()]))
                cond.append(db.joinOr([tableContractTariff['endDate'].dateGe(self._endDateForTariff),
                                       tableContractTariff['endDate'].isNull()]))

        if self._MKB and mkbCond and not operativeMes:
            tableMESMkb = db.table('mes.MES_mkb')
            if mkbCond == 2:  # строгое соответствие
                subCond = tableMESMkb['mkb'].inlist([self._MKB, MKBwithoutSubclassification(self._MKB)])
            else:  # по рубрике
                subCond = tableMESMkb['mkb'].like(self._MKB[:3] + '%')
            subCond = [tableMESMkb['master_id'].eq(tableMES['id']),
                       subCond]
            cond.append(db.existsStmt(tableMESMkb, subCond))

        # atronah: None - не фильтровать по списку id. [] - фильтровать по пустому списку (т.е. запрет выбора МЭС)
        if isinstance(self._availableIdList, list):
            cond.append(tableMES['id'].inlist(self._availableIdList))
        cond.append(tableMES['deleted'].eq(0))

        idList = []
        order = 'mes.MES.code, mes.MES.id'
        if (useAge and self._clientAge):
            recordList = db.getRecordList(queryTable,
                                          cols=[tableMES['id'],
                                                tableServiceProfile['age']],
                                          where=cond,
                                          order=order)
            for record in recordList:
                mesId = forceRef(record.value('id'))
                ageString = forceString(record.value('age'))
                if mesId in idList:
                    continue
                if ageString:
                    ageSelectors = parseAgeSelector(ageString, isExtend=True)
                    if checkExtendedAgeSelector(ageSelectors, self._clientAge):
                        idList.append(mesId)
                else:
                    idList.append(mesId)
            if not idList:
                regionalCheck = (QtGui.qApp.region() == u'91'
                                 and hasattr(self, '_eventTypeId')
                                 and hasattr(self, '_clientId')
                                 and getEventCode(self._eventTypeId).lower() in [u'дв1', u'дв2']
                                 and hasSocStatus(self._clientId, {'specialCase': ['10', '11', '12']}))
                if regionalCheck:
                    distFunction = lambda record: findExtendedAgeSelectorDist(
                        parseAgeSelector(forceString(record.value('age')), isExtend=True), self._clientAge)
                    nearestRecord = argMin(recordList, key=distFunction)
                    idList = [forceInt(nearestRecord.value('id'))] if nearestRecord else []
        else:
            idList = db.getDistinctIdList(queryTable, tableMES['id'].name(),
                                          where=cond,
                                          order=order)
        return idList

    def setup(self, clientSex, clientAge, clientId, eventProfileId, eventTypeId, mesCodeTemplate, mesNameTemplate,
              specialityId, contractId, MKB, mesId, availableMesIdList=None, endDateForTariff=None,
              actionTypeIdList=None, date=None):
        self._clientSex = clientSex
        self._clientAge = clientAge
        self._clientId = clientId
        self._eventProfileId = eventProfileId
        self._eventTypeId = eventTypeId
        self._mesCodeTemplate = mesCodeTemplate
        self._mesNameTemplate = mesNameTemplate
        self._specialityId = specialityId
        self._contractId = contractId
        self._endDateForTariff = endDateForTariff
        self._MKB = MKB
        self._id = mesId
        self._availableIdList = availableMesIdList
        self._actionTypeIdList = actionTypeIdList
        self._checkDate = date
        if actionTypeIdList is not None:
            self.chkOperativeMes.setVisible(True)
        self.on_buttonBox_apply()

    def setCheckBoxes(self, dicTag):
        self._dicTag = dicTag
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'MESCBCheckBoxes', {})
        checkList = getPref(preferences, forceString(self._dicTag), {})
        if checkList:
            self.chkSex.setChecked(getPrefBool(checkList, 'sex', False))
            self.chkAge.setChecked(getPrefBool(checkList, 'age', False))
            self.chkEventProfile.setChecked(getPrefBool(checkList, 'eventProfile', False))
            self.chkMesCodeTemplate.setChecked(getPrefBool(checkList, 'mesCodeTemplate', False))
            self.chkMesNameTemplate.setChecked(getPrefBool(checkList, 'mesNameTemplate', False))
            self.chkSpeciality.setChecked(getPrefBool(checkList, 'speciality', False))
            self.chkContract.setChecked(getPrefBool(checkList, 'contract', False))
            self.cmbMKB.setCurrentIndex(getPrefInt(checkList, 'MKB', 0))

    def getCheckBoxes(self):
        if self._dicTag:
            checkList = {}
            setPref(checkList, 'sex', self.chkSex.isChecked())
            setPref(checkList, 'age', self.chkAge.isChecked())
            setPref(checkList, 'eventProfile', self.chkEventProfile.isChecked())
            setPref(checkList, 'mesCodeTemplate', self.chkMesCodeTemplate.isChecked())
            setPref(checkList, 'mesNameTemplate', self.chkMesNameTemplate.isChecked())
            setPref(checkList, 'speciality', self.chkSpeciality.isChecked())
            setPref(checkList, 'contract', self.chkContract.isChecked())
            setPref(checkList, 'MKB', self.cmbMKB.currentIndex())
            preferences = {}
            setPref(preferences, forceString(self._dicTag), checkList)
            setPref(QtGui.qApp.preferences.windowPrefs, 'MESCBCheckBoxes', preferences)
