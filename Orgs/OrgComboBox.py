# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Accounting.Utils import CTariff
from OrganisationComboBoxPopup import COrganisationComboBoxPopup
from Utils import getOrganisationInfo
from library.DbComboBox import CAbstractDbComboBox, CAbstractDbModel, CDbComboBox, CDbData, CDbModel
from library.InDocTable import CInDocTableCol
from library.Utils import forceRef, forceString, quote, toVariant


class CDbModelSearch(CDbModel):
    def __init__(self, parent):
        CDbModel.__init__(self, parent)

    def keyboardSearch(self, search):
        if self.dbDataAvailable():
            length = len(self.dbdata.strList) - 1
            step = 1
            lengthSearch = len(search)
            while step <= length:
                s = forceString(self.dbdata.strList[step])
                lengthString = len(s)
                sLengthSearch = lengthSearch
                i = 0
                while i <= lengthString:
                    s2 = s[i:sLengthSearch]
                    if s2.upper() == search:
                        return step
                    else:
                        i += 1
                        sLengthSearch += 1
                step += 1
        else:
            return -1


class COrgComboBox(CDbComboBox):
    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setModel(CDbModelSearch(self))
        self.setNameField('shortName')
        self.setAddNone(True)
        self.setTable('Organisation')


class COrgInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width):
        CInDocTableCol.__init__(self, title, fieldName, width)

    def toString(self, val, record):
        orgId = forceRef(val)
        info = getOrganisationInfo(orgId)
        if info:
            return toVariant(info.get('shortName', u'не задано'))
        return QtCore.QVariant(u'не задано')

    def createEditor(self, parent):
        editor = COrgComboBox(parent)
        editor.setAddNone(True, u'не задано')
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())


class CInsurerComboBox(CDbComboBox):
    insurerFilter = 'isInsurer = 1 AND deleted = 0'

    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setNameField('CONCAT(infisCode,\'| \', shortName)')
        self.setAddNone(True)
        self.setFilter(self.insurerFilter)
        self.setTable('Organisation')
        self._popup = COrganisationComboBoxPopup(self, self.insurerFilter, useInsuranceAreaModel=False)
        self._popup.tabWidget.setTabText(0, u'&СМО')

    def showPopup(self):
        self.__searchString = ''
        self.connect(self._popup, QtCore.SIGNAL('itemComboBoxSelected(int)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()

    def setPolicyTypeFilter(self, isCompulsory=True):
        u"""
            i2767.
            Организация отображается в комбобоксе "ОМС" (рег. карта пациента), если в справочнике организаций у неё стоят чекбоксы:
                [v] Страховая компания, [v] ОМС, [ ] ДМС
            То же самое для "ДМС".
            Если чекбоксы "ОМС", "ДМС" одновременно включены/выключены, компания отображается в обоих комбобоксах "ОМС", "ДМС"
        """
        db = QtGui.qApp.db
        Organisation = db.table('Organisation')

        policyTypeCond = db.joinAnd([
            Organisation['deleted'].eq(0),
            Organisation['isInsurer'].eq(1),
            db.joinOr([
                Organisation['isCompulsoryInsurer'].eq(1 if isCompulsory else 0),
                Organisation['isVoluntaryInsurer'].eq(0 if isCompulsory else 1)
            ])
        ])
        self._popup.setOrganisationFilter(policyTypeCond)

    def setSerialFilter(self, serial):
        self._popup.setSerialFilter(serial)

    def setAreaFilter(self, areaList):
        if len(areaList):
            area = areaList[0]
            self._popup.chkArea.setChecked(True)
            self._popup.cmbArea.setEnabled(True)
            self._popup.cmbArea.setCode(area)
            self._popup.setAreaFilter([area])
            self._popup.model.update()
            self._popup.on_buttonBox_apply()

    def setValue(self, itemId):
        if itemId == 0:
            itemId = None
        CDbComboBox.setValue(self, itemId)


class CInsurerInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width):
        CInDocTableCol.__init__(self, title, fieldName, width)

    def toString(self, val, record):
        result = QtGui.qApp.db.translate('Organisation', 'id', val, 'CONCAT(infisCode,\'| \', shortName)')
        return result if result else QtCore.QVariant(u'не задано')

    def createEditor(self, parent):
        editor = CInsurerComboBox(parent)
        editor.setAddNone(True, u'не задано')
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())


class CArmyOrgComboBox(CDbComboBox):
    nameField = 'CONCAT(infisCode, \' | \', shortName)'
    _filter = 'isArmyOrg != 0'

    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setNameField(CArmyOrgComboBox.nameField)
        self.setAddNone(True)
        self.setFilter(CArmyOrgComboBox._filter)
        self.setTable('Organisation')


class CPolyclinicComboBox(CDbComboBox):
    nameField = 'CONCAT(infisCode, \' | \', shortName)'
    _filter = 'isMedical != 0'

    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setNameField(CPolyclinicComboBox.nameField)
        self.setAddNone(True)
        self.setFilter(CPolyclinicComboBox._filter)
        self.setTable('Organisation')


class CPolyclinicExtendedComboBox(CDbComboBox):
    nameField = 'CONCAT(infisCode, \' | \', shortName)'
    _filter = 'deleted = 0'  # 'isMedical != 0 AND deleted = 0'

    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setNameField(CPolyclinicExtendedComboBox.nameField)
        self.setAddNone(True)
        self.setFilter(CPolyclinicExtendedComboBox._filter)
        self.setTable('Organisation')
        self._popup = COrganisationComboBoxPopup(self, CPolyclinicExtendedComboBox._filter)
        self._popup.tabWidget.setTabText(0, u'&ЛПУ')

    def showPopup(self):
        self.__searchString = ''
        self.connect(self._popup, QtCore.SIGNAL('itemComboBoxSelected(int)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()

    def setSerialFilter(self, serial):
        self._popup.setSerialFilter(serial)

    def setAreaFilter(self, areaList):
        self._popup.setAreaFilter(areaList)

    def setValue(self, itemId):
        if itemId == 0:
            itemId = None
        CDbComboBox.setValue(self, itemId)


class CPolyclinicExtendedInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width):
        CInDocTableCol.__init__(self, title, fieldName, width)
        self._cache = {}

    def getData(self, val):
        result = QtGui.qApp.db.translate('Organisation', 'id', val, 'CONCAT(infisCode,\'| \', shortName)')
        return result if result else QtCore.QVariant(u'не задано')

    def toString(self, val, record):
        key = forceRef(val)
        if key not in self._cache:
            self._cache[key] = self.getData(val)
        return self._cache[key]

    def createEditor(self, parent):
        editor = CPolyclinicExtendedComboBox(parent)
        editor.setAddNone(True, u'не задано')
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())

    def invalidateCache(self):
        self._cache = {}


class COrgAccComboBox(CDbComboBox):
    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setNameField('name')
        self.setAddNone(True)
        self.setFilter('1=0')
        self.setTable('Organisation_Account')
        self.__orgId = None

    def setOrgId(self, orgId):
        if self.__orgId != orgId:
            if orgId:
                self.setAddNone(False)
                self.setFilter('organisation_id=\'%d\'' % orgId)
            else:
                self.setAddNone(True)
                self.setFilter('1=0')
            self.__orgId = orgId
            self.model().reset()
            if self.model().rowCount(QtCore.QModelIndex()) > 0:
                self.setCurrentIndex(0)


class CContractDbData(CDbData):
    def __init__(self):
        CDbData.__init__(self)
        self.financeList = []

    def select(self, cond):
        self.selectInt(True, True, cond)
        if self.idList:
            self.appendAssignedContracts(cond)
            return
        self.selectInt(True, False, cond)
        if self.idList:
            self.appendAssignedContracts(cond)
            return
        self.selectInt(False, True, cond)
        if self.idList:
            self.appendAssignedContracts(cond)
            return
        self.selectInt(False, False, cond)
        self.appendAssignedContracts(cond)

    def appendAssignedContracts(self, cond):
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        tableFinance = db.table('rbFinance')
        filter = []
        if cond.clientId:
            filter.append(tableContract['assignedClient_id'].eq(cond.clientId))
            filter.append(db.joinOr([tableContract['assignedBegDate'].le(cond.begDate),
                                     tableContract['assignedBegDate'].isNull()
                                     ]))
            filter.append(db.joinOr([tableContract['assignedEndDate'].ge(cond.endDate),
                                     tableContract['assignedEndDate'].isNull()
                                     ]))
        self.appendContractsByFilter(filter)

    def selectInt(self, strictEventType, strictContingent, cond):
        from Events.Utils import getEventFinanceId

        # нужен запрос типа
        #    SELECT *
        #    FROM Contract
        #    WHERE
        #      recipient_id = orgId
        #      AND ((EXISTS (SELECT id
        #                    FROM Contract_Specification
        #                    WHERE
        #                        Contract_Specification.master_id=Contract.id
        #                        AND Contract_Specification.eventType_id = $eventTypeId
        #                   )
        #           ) OR
        #           (NOT EXISTS (
        #                    SELECT id
        #                    FROM Contract_Specification
        #                    WHERE Contract_Specification.master_id=Contract.id
        #                       )
        #           )
        #          )
        #      AND ((EXISTS (SELECT id
        #                    FROM Contract_Contingent
        #                    WHERE
        #                        Contract_Contingent.master_id=Contract.id
        #                        AND (Contract_Contingent.org_id = $clientOrgId OR Contract_Contingent.org_id IS NULL)
        #                   )
        #           ) OR
        #           (NOT EXISTS (
        #                    SELECT id
        #                    FROM Contract_Contingent
        #                    WHERE Contract_Contingent.master_id=Contract.id
        #                       )
        #           )
        #          )
        #      AND Contract.finance_id = $eventType.financeId
        #      AND Contract.begDate <= begDate
        #      AND Contract.endDate >= endDate
        # с учётом того что параметры функции могут быть нулями
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        tableFinance = db.table('rbFinance')
        filter = []
        # if cond.orgId:
        #   filter.append(tableContract['recipient_id'].eq(cond.orgId))
        if cond.financeId:
            filter.append(tableContract['finance_id'].eq(cond.financeId))
        if cond.eventTypeId:
            tableContractSpecification = db.table('Contract_Specification')
            condInContract = db.joinAnd([tableContractSpecification['master_id'].eq(tableContract['id']),
                                         tableContractSpecification['deleted'].eq(0)])
            if strictEventType:
                filterEventType = [condInContract, tableContractSpecification['eventType_id'].eq(cond.eventTypeId)]
                condEventType = db.existsStmt(tableContractSpecification, filterEventType)
            else:
                filterEventType = [condInContract, tableContractSpecification['eventType_id'].isNotNull()]
                condEventType = 'NOT ' + db.existsStmt(tableContractSpecification, filterEventType)
            filter.append(condEventType)
            financeId = getEventFinanceId(cond.eventTypeId)
            if financeId:
                filter.append(tableContract['finance_id'].eq(financeId))
        if cond.actionTypeId and cond.financeId:
            tableActionTypeService = db.table('ActionType_Service')
            tableContractTariff = db.table('Contract_Tariff')
            tableATCT = tableContractTariff.leftJoin(tableActionTypeService, tableActionTypeService['service_id'].eq(
                tableContractTariff['service_id']))
            actionFilter = [tableContractTariff['deleted'].eq(0),
                            tableContractTariff['master_id'].eq(tableContract['id']),
                            tableActionTypeService['master_id'].eq(cond.actionTypeId),
                            tableContractTariff['tariffType'].inlist(
                                [CTariff.ttActionAmount, CTariff.ttHospitalBedService]),
                            db.joinOr([tableActionTypeService['finance_id'].eq(cond.financeId),
                                       'ActionType_Service.finance_id IS NULL AND NOT EXISTS(SELECT 1 FROM ActionType_Service AS ATS WHERE ATS.master_id=%d AND ATS.finance_id=%d)' % (
                                           cond.actionTypeId, cond.financeId)
                                       ]
                                      )
                            ]
            filter.append(db.existsStmt(tableATCT, db.joinAnd(actionFilter)))
        tableContractContingent = db.table('Contract_Contingent')
        condInContract = db.joinAnd([tableContractContingent['master_id'].eq(tableContract['id']),
                                     tableContractContingent['deleted'].eq(0)])
        existContingent = db.existsStmt(tableContractContingent, condInContract)
        if strictContingent:
            contingentFilter = [condInContract,
                                tableContractContingent['sex'].inlist([0, cond.clientSex])
                                ]
            if cond.clientOrgId:
                contingentFilter.append(db.joinOr([tableContractContingent['org_id'].eq(cond.clientOrgId),
                                                   tableContractContingent['org_id'].isNull()
                                                   ]))
            if cond.clientPolicyInfoList:
                contingentFilterByPolicy = []
                for insurerId, policyTypeId in cond.clientPolicyInfoList:
                    subFilterContingent = []
                    if insurerId:
                        subFilterContingent.append(db.joinOr([tableContractContingent['insurer_id'].eq(insurerId),
                                                              tableContractContingent['insurer_id'].isNull()
                                                              ]))
                        subFilterContingent.append(
                            'insurerServiceAreaMatch(%d, Contract_Contingent.serviceArea, %s, %s)' %
                            (insurerId,
                             quote(QtGui.qApp.defaultKLADR()),
                             quote(QtGui.qApp.provinceKLADR()),
                             )
                            )
                    else:
                        subFilterContingent.append(tableContractContingent['insurer_id'].isNull())
                        subFilterContingent.append(
                            'insurerServiceAreaMatch(NULL, Contract_Contingent.serviceArea, %s, %s)' %
                            (quote(QtGui.qApp.defaultKLADR()),
                             quote(QtGui.qApp.provinceKLADR()),
                             )
                            )
                    if policyTypeId:
                        subFilterContingent.append(db.joinOr([tableContractContingent['policyType_id'].eq(policyTypeId),
                                                              tableContractContingent['policyType_id'].isNull()
                                                              ]))
                    else:
                        subFilterContingent.append(tableContractContingent['policyType_id'].isNull())
                    if subFilterContingent:
                        contingentFilterByPolicy.append(db.joinAnd(subFilterContingent))
                if contingentFilterByPolicy:
                    contingentFilter.append(db.joinOr(contingentFilterByPolicy))
            condContingentMatch = db.existsStmt(tableContractContingent, contingentFilter)
            condContingent = db.joinOr(['NOT ' + existContingent, condContingentMatch])
            filter.append(condContingent)
        if cond.begDate and not cond.begDate.isNull():
            filter.append(tableContract['begDate'].le(cond.begDate))
        if cond.endDate and not cond.endDate.isNull():
            filter.append(tableContract['endDate'].ge(cond.endDate))
        if cond.checkMaxClients:
            filter.append(
                db.joinOr([tableContract['maxClients'].eq(0),
                           'Contract.maxClients > (SELECT COUNT(DISTINCT Event.client_id) FROM Event WHERE Event.contract_id = Contract.id AND Event.deleted = 0)']))

        self.idList = []
        self.strList = []
        self.financeList = []
        self.appendContractsByFilter(filter)

    def appendContractsByFilter(self, filter):
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        tableFinance = db.table('rbFinance')
        stmt = db.selectStmt(tableContract.leftJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id'])),
                             [tableContract['id'], tableContract['number'], tableContract['date'],
                              tableContract['resolution'],
                              tableFinance['code'].alias('finance')
                              ],
                             filter,
                             order=[tableFinance['idx'].name(), tableFinance['code'].name() + ' DESC',
                                    tableContract['number'].name(), tableContract['date'].name(),
                                    tableContract['resolution'].name()]
                             )
        query = db.query(stmt)
        while query.next():
            record = query.record()
            id = record.value('id').toInt()[0]
            if id not in self.idList:
                if QtGui.qApp.checkGlobalPreference('47', u'да'):
                    nameList = ['number', 'date', 'resolution']
                else:
                    nameList = ['number', 'resolution']
                str = ' '.join([forceString(record.value(name)) for name in nameList])
                finance = forceString(record.value('finance'))
                self.idList.append(id)
                self.strList.append(str)
                self.financeList.append(finance)

    def onlyOneWithSameFinance(self, index):
        if 0 <= index < len(self.financeList):
            return self.financeList.count(self.financeList[index])
        else:
            return False

    def getContractIdByFinance(self, financeCode):
        if financeCode in self.financeList:
            index = self.financeList.index(financeCode)
            return self.idList[index]
        return None


class CContractDbModel(CAbstractDbModel):
    def __init__(self, parent):
        CAbstractDbModel.__init__(self, parent)
        self.orgId = None
        self.clientId = None
        self.clientSex = None
        self.clientAge = None
        self.clientOrgId = None
        self.clientPolicyInfoList = None
        self.financeId = None
        self.eventTypeId = None
        self.actionTypeId = None
        self.begDate = None
        self.endDate = None
        self.checkMaxClients = False

    def initDbData(self):
        self.dbdata = CContractDbData()
        if self.orgId and (self.eventTypeId or self.financeId) and self.clientId:
            self.dbdata.select(self)

    def setOrgId(self, orgId):
        if self.orgId != orgId:
            self.orgId = orgId
            self.dbdata = None
            self.reset()

    def setClientInfo(self, clientId, sex=None, age=None, orgId=None, policyInfoList=None):
        if (self.clientId != clientId
                or self.clientSex != sex
                or self.clientAge != age
                or self.clientOrgId != orgId
                or self.clientPolicyInfoList != policyInfoList):
            self.clientId = clientId
            self.clientSex = sex
            self.clientAge = age
            self.clientOrgId = orgId
            self.clientPolicyInfoList = policyInfoList
            self.dbdata = None
            self.reset()

    def setFinanceId(self, financeId):
        if self.financeId != financeId:
            self.financeId = financeId
            self.dbdata = None
            self.reset()

    def setEventTypeId(self, eventTypeId):
        if self.eventTypeId != eventTypeId:
            self.eventTypeId = eventTypeId
            self.dbdata = None
            self.reset()

    def setActionTypeId(self, actionTypeId):
        if self.actionTypeId != actionTypeId:
            self.actionTypeId = actionTypeId
            self.dbdata = None
            self.reset()

    def setBegDate(self, begDate):
        if self.begDate != begDate:
            self.begDate = begDate
            self.dbdata = None
            self.reset()

    def setEndDate(self, endDate):
        if self.endDate != endDate:
            self.endDate = endDate
            self.dbdata = None
            self.reset()

    def setCheckMaxClients(self, check):
        if self.checkMaxClients != check:
            self.checkMaxClients = check
            self.dbdata = None
            self.reset()

    def onlyOneWithSameFinance(self, index):
        if self.dbdata:
            return self.dbdata.onlyOneWithSameFinance(index)
        else:
            return False

    def getContractIdByFinance(self, financeCode):
        if self.dbdata:
            return self.dbdata.getContractIdByFinance(financeCode)
        return None


class CContractComboBox(CAbstractDbComboBox):
    __pyqtSignals__ = ('valueChanged()',
                       )

    def __init__(self, parent=None):
        CAbstractDbComboBox.__init__(self, parent)
        self.__model = CContractDbModel(self)
        self.setModel(self.__model)
        self.__prevValue = None
        self.connect(self, QtCore.SIGNAL('currentIndexChanged(int)'), self.onCurrentIndexChanged)

    def getWeakValue(self):
        if self.__model.dbdata:
            return self.value()
        else:
            return None

    def setCurrentIfOnlyOne(self):
        n = self.__model.rowCount()
        if n == 1:
            self.setCurrentIndex(0)
        elif n > 1 and self.__model.onlyOneWithSameFinance(0):
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(-1)

    def setOrgId(self, orgId):
        self.__model.setOrgId(orgId)

    def setClientInfo(self, clientId, sex, age, orgId, policyInfoList):
        self.__model.setClientInfo(clientId, sex, age, orgId, policyInfoList)

    def setFinanceId(self, financeId):
        self.__model.setFinanceId(financeId)

    def setEventTypeId(self, eventTypeId):
        self.__model.setEventTypeId(eventTypeId)

    def setActionTypeId(self, actionTypeId):
        self.__model.setActionTypeId(actionTypeId)

    def setBegDate(self, begDate):
        self.__model.setBegDate(begDate)
        self.setCurrentIfOnlyOne()
        self.conditionalEmitValueChanged()

    def setEndDate(self, endDate):
        self.__model.setEndDate(endDate)
        self.setCurrentIfOnlyOne()
        self.conditionalEmitValueChanged()

    def setCheckMaxClients(self, check):
        self.__model.setCheckMaxClients(check)

    def setCurrentIndex(self, index):
        CAbstractDbComboBox.setCurrentIndex(self, index)
        self.conditionalEmitValueChanged()

    def onCurrentIndexChanged(self, index):
        self.conditionalEmitValueChanged()

    def setValue(self, value):
        CAbstractDbComboBox.setValue(self, value)
        self.conditionalEmitValueChanged()

    def conditionalEmitValueChanged(self):
        value = self.getWeakValue()
        if self.__prevValue != value:
            self.__prevValue = value
            self.emit(QtCore.SIGNAL('valueChanged()'))

    def getContractIdByFinance(self, financeCode):
        return self.__model.getContractIdByFinance(financeCode)


class CIndependentContractComboBox(CDbComboBox):
    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)
        self.setTable('Contract',
                      nameField='CONCAT_WS(\' \',grouping, number, DATE_FORMAT(date,\'%d:%m:%Y`\'), resolution)')
        self.setAddNone(True, u'не задано')
        self.begDate = QtCore.QDate.currentDate()
        self.endDate = QtCore.QDate.currentDate()
        self.financeId = None
        self.updateFilter()

    def setBegDate(self, date):
        if date != self.begDate:
            self.begDate = date
            self.updateFilter()

    def setEndDate(self, date):
        if date != self.endDate:
            self.begDate = date
            self.updateFilter()

    def setFinanceId(self, financeId):
        if financeId != self.financeId:
            self.financeId = financeId
            self.updateFilter()

    def updateFilter(self):
        db = QtGui.qApp.db
        value = self.value()
        tableContract = db.table('Contract')
        cond = [tableContract['endDate'].dateGe(self.begDate),
                tableContract['begDate'].dateLe(self.endDate),
                tableContract['recipient_id'].eq(QtGui.qApp.currentOrgId())]
        if self.financeId:
            cond.append(tableContract['finance_id'].eq(self.financeId))
        self.setFilter(db.joinAnd(cond))
        self.setValue(value)
