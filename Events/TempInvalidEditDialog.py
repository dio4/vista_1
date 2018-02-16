# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.MKBInfo import CMKBInfo
from Events.TempInvalid import Busyness, CTempInvalidPeriodModel, formatWorkTempInvalid, requiredDiagnosis, requiredOtherPerson
from Events.TempInvalidInfo import CTempInvalidDocTypeInfo, CTempInvalidExtraReasonInfo, CTempInvalidInfo, \
    CTempInvalidReasonInfo
from Events.Utils import getAvailableCharacterIdByMKB, getDiagnosisId2, specifyDiagnosis
from Exchange.R78.FssLn.LnService import LnService
from Registry.Utils import CClientInfo, getClientWork
from Ui_TempInvalidEditDialog import Ui_TempInvalidEditDialog
from Users.Rights import urRegWriteInsurOfficeMark
from library.DialogBase import CDialogBase
from library.ItemsListDialog import CItemEditorBaseDialog
from library.PrintInfo import CDateInfo, CInfoContext
from library.PrintTemplates import applyTemplate, getPrintButton
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, formatSex, toVariant
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, getRBComboBoxValue, getSpinBoxValue, \
    getWidgetValue, setCheckBoxValue, setComboBoxValue, setLineEditValue, setRBComboBoxValue, setSpinBoxValue, setWidgetValue


class CTempInvalidEditDialog(CItemEditorBaseDialog, Ui_TempInvalidEditDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'TempInvalid')
        self.modelPeriods = CTempInvalidPeriodModel(self)
        self.modelPeriods.setObjectName('modelPeriods')
        self.btnPrint = getPrintButton(self, 'tempInvalid', u'Печать')
        self.btnPrint.setObjectName('btnPrint')
        self.btnPrint.setShortcut('F6')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Документ временной нетрудоспособности')
        self.cmbBusyness.setEnum(Busyness)
        self.tblPeriods.setModel(self.modelPeriods)
        self.tblPeriods.addPopupDelRow()
        self.modelPeriods.setEventEditor(self)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.clientId = None
        self.diagnosisId = None
        self.prevId = None
        self.orgId = QtGui.qApp.currentOrgId()
        self.personId = None
        self.caseBegDate = None
        self.prolonging = False
        self.saveProlonging = False
        self.closed = 0
        self.setupDirtyCather()
        self.clientSex = None
        self.clientAge = None
        self.edtCaseBegDate.setDate(self.caseBegDate)
        self.edtCaseBegDate.setEnabled(False)
        self.chkInsuranceOfficeMark.setEnabled(QtGui.qApp.userHasRight(urRegWriteInsurOfficeMark))
        self.blankParams = {}
        self.defaultBlankMovingId = None
        self.mapSpecialityIdToDiagFilter = {}
        self.modifiableDiagnosisesMap = {}
        self.cmbDiseaseCharacter.setTable('rbDiseaseCharacter', order='code')

        # i4725@0019089: hide useless elements
        self.lblOtherSex.setVisible(False)
        self.cmbOtherSex.setVisible(False)
        self.lblOtherAge.setVisible(False)
        self.edtOtherAge.setVisible(False)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setCheckBoxValue(self.chkInsuranceOfficeMark, record, 'insuranceOfficeMark')
        self.closed = forceInt(record.value('closed'))
        self.clientId = forceRef(record.value('client_id'))
        self.diagnosisId = forceRef(record.value('diagnosis_id'))
        self.setType(forceInt(record.value('type')))
        setRBComboBoxValue(self.cmbDoctype, record, 'doctype_id')
        setRBComboBoxValue(self.cmbReason, record, 'tempInvalidReason_id')
        setRBComboBoxValue(self.cmbExtraReason, record, 'tempInvalidExtraReason_id')
        setWidgetValue(self.cmbBusyness, record, 'busyness')
        setLineEditValue(self.edtPlaceWork, record, 'placeWork')
        setLineEditValue(self.edtNumber, record, 'number')
        setComboBoxValue(self.cmbOtherSex, record, 'sex')
        setSpinBoxValue(self.edtOtherAge, record, 'age')
        setCheckBoxValue(self.chkGovEmoploymentService, record, 'employmentService')
        setLineEditValue(self.edtMainNumber, record, 'mainNumber')
        self.modelPeriods.loadItems(self.itemId())
        self.setEnabledWidget(
            self.chkInsuranceOfficeMark.isChecked(),
            [
                self.cmbDoctype,
                self.cmbReason,
                self.cmbExtraReason,
                self.edtNumber,
                self.edtDiagnosis,
                self.cmbDiseaseCharacter,
                self.chkInsuranceOfficeMark,
                self.tblPeriods
            ]
        )

        db = QtGui.qApp.db
        MKB = forceString(db.translate('Diagnosis', 'id', self.diagnosisId, 'MKB'))
        self.edtDiagnosis.setText(MKB)

        table = db.table('TempInvalid')
        condDeleted = table['deleted'].eq(0)
        condClient = table['client_id'].eq(self.clientId)
        prevCond = [
            condDeleted,
            condClient,
            table['closed'].eq(2),
            table['endDate'].eq(forceDate(record.value('begDate')).addDays(-1))
        ]
        prevRecord = db.getRecordEx(table, '*', prevCond, 'endDate DESC')
        self.setPrev(prevRecord)
        self.updateLength()
        self.btnTempInvalidProlong.setEnabled(self.closed == 0)
        self.prolonging = False
        self.defaultBlankMovingId = None

    def setEnabledWidget(self, checked, listWidget=None):
        if not listWidget:
            listWidget = []
        enabled = QtGui.qApp.userHasRight(urRegWriteInsurOfficeMark)
        otherPersonEnabled = requiredOtherPerson(self.cmbReason.value())
        if checked:
            for widget in listWidget:
                widget.setEnabled(enabled)
            self.cmbOtherSex.setEnabled(otherPersonEnabled and enabled)
            self.edtOtherAge.setEnabled(otherPersonEnabled and enabled)
            if self.btnTempInvalidProlong.isEnabled():
                closed = self.modelPeriods.getTempInvalidClosedStatus()
                self.btnTempInvalidProlong.setEnabled(enabled and closed == 0)
        else:
            self.cmbOtherSex.setEnabled(otherPersonEnabled)
            self.edtOtherAge.setEnabled(otherPersonEnabled)
            self.chkInsuranceOfficeMark.setEnabled(enabled)

    def getBlankParams(self):
        self.defaultBlankMovingId = None
        self.blankParams = {}

        db = QtGui.qApp.db
        tableTempInvalid = db.table('TempInvalid')

        blankIdList = []
        docTypeId = self.cmbDoctype.value()
        if docTypeId:
            personId = QtGui.qApp.userId

            tableBTI = db.table('rbBlankTempInvalids')
            tableBTIParty = db.table('BlankTempInvalid_Party')
            tableBTIMoving = db.table('BlankTempInvalid_Moving')
            tablePerson = db.table('Person')

            orgStructureId = None
            if personId:
                orgStructRecord = db.getRecordEx(
                    tablePerson,
                    [tablePerson['orgStructure_id']], [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId)]
                )
                orgStructureId = forceRef(orgStructRecord.value('orgStructure_id')) if orgStructRecord else None
            cols = [tableBTIMoving['id'].alias('blankMovingId'),
                    tableBTI['checkingSerial'],
                    tableBTI['checkingNumber'],
                    tableBTI['checkingAmount'],
                    tableBTIParty['serial'],
                    tableBTIMoving['numberFrom'],
                    tableBTIMoving['numberTo'],
                    tableBTIMoving['returnAmount'],
                    tableBTIMoving['used'],
                    tableBTIMoving['received']
                    ]
            cond = [tableBTI['doctype_id'].eq(docTypeId),
                    tableBTIParty['deleted'].eq(0),
                    tableBTIMoving['deleted'].eq(0)
                    ]
            order = []

            if orgStructureId:
                orgStructureIdList = db.getTheseAndParents('OrgStructure', 'parent_id',
                                                           [orgStructureId]) if orgStructureId else []
            else:
                orgStructureIdList = []

            if personId and orgStructureIdList:
                cond.append(db.joinOr([tableBTIMoving['person_id'].eq(personId),
                                       tableBTIMoving['orgStructure_id'].inlist(orgStructureIdList)]))
                order.append(tableBTIMoving['person_id'])
            elif personId:
                cond.append(tableBTIMoving['person_id'].eq(personId))
            elif orgStructureIdList:
                cond.append(tableBTIMoving['orgStructure_id'].inlist(orgStructureIdList))
            queryTable = tableBTI.innerJoin(tableBTIParty, tableBTIParty['doctype_id'].eq(tableBTI['id']))
            queryTable = queryTable.innerJoin(tableBTIMoving, tableBTIMoving['blankParty_id'].eq(tableBTIParty['id']))
            order.extend([
                tableBTI['checkingSerial'],
                tableBTI['checkingNumber'],
                tableBTI['checkingAmount'].desc()
            ])
            for record in db.iterRecordList(queryTable, cols, cond, order):
                blankMovingId = forceRef(record.value('blankMovingId'))
                self.blankParams[blankMovingId] = {
                    'returnAmount': forceInt(record.value('returnAmount')),
                    'used': forceInt(record.value('used')),
                    'received': forceInt(record.value('received')),
                    'checkingSerial': forceInt(record.value('checkingSerial')),
                    'checkingNumber': forceInt(record.value('checkingNumber')),
                    'checkingAmount': forceInt(record.value('checkingAmount')),
                    'serial': forceString(record.value('serial')),
                    'numberFrom': forceInt(record.value('numberFrom')),
                    'numberTo': forceInt(record.value('numberTo'))
                }
                blankIdList.append(blankMovingId)

    def setType(self, type_):
        self.type_ = type_
        filter = 'type=%d' % self.type_
        self.cmbDoctype.setTable('rbTempInvalidDocument', False, filter)
        self.cmbReason.setTable('rbTempInvalidReason', False, filter)
        self.cmbExtraReason.setTable('rbTempInvalidExtraReason', True, filter)
        self.modelPeriods.setType(self.type_)

        for widget in [self.lblOtherSex, self.cmbOtherSex,
                       self.lblOtherAge, self.edtOtherAge]:
            widget.setVisible(self.type_ == 0)
        if self.type_ == 0:
            self.cmbDoctype.setCode(QtGui.qApp.tempInvalidDoctype())
            self.cmbReason.setCode(QtGui.qApp.tempInvalidReason())
        if (self.clientId
                and not self.edtPlaceWork.text()
                and (self.cmbBusyness.value() in (Busyness.NotSet,
                                                  Busyness.Main))):
            work = formatWorkTempInvalid(getClientWork(self.clientId))
            if work:
                self.edtPlaceWork.setText(work)
                self.cmbBusyness.setValue(Busyness.Main)
        self.getBlankParams()

    def setPrev(self, prevRecord):
        if prevRecord:
            number = forceString(prevRecord.value('number'))
            self.prevId = forceRef(prevRecord.value('id'))
            self.caseBegDate = forceDate(prevRecord.value('caseBegDate'))
        else:
            number = ''
            self.prevId = None
            self.caseBegDate = None

        self.lblPrevNumberValue.setText(number)
        self.edtCaseBegDate.setDate(self.caseBegDate)
        self.edtCaseBegDate.setEnabled(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        db = QtGui.qApp.db
        tableTempInvalid = db.table('TempInvalid')
        tableBTIMoving = db.table('BlankTempInvalid_Moving')
        itemId = self.itemId()
        record.setValue('type', toVariant(self.type_))
        record.setValue('client_id', toVariant(self.clientId))
        getRBComboBoxValue(self.cmbDoctype, record, 'doctype_id')
        getRBComboBoxValue(self.cmbReason, record, 'tempInvalidReason_id')
        getRBComboBoxValue(self.cmbExtraReason, record, 'tempInvalidExtraReason_id')
        getWidgetValue(self.cmbBusyness, record, 'busyness')
        getLineEditValue(self.edtPlaceWork, record, 'placeWork')
        getLineEditValue(self.edtNumber, record, 'number')
        getComboBoxValue(self.cmbOtherSex, record, 'sex')
        getSpinBoxValue(self.edtOtherAge, record, 'age')
        getCheckBoxValue(self.chkGovEmoploymentService, record, 'employmentService')
        getCheckBoxValue(self.chkInsuranceOfficeMark, record, 'insuranceOfficeMark')
        fullLength, externalLength = self.modelPeriods.calcLengths()
        record.setValue('begDate', toVariant(self.modelPeriods.begDate()))
        record.setValue('endDate', toVariant(self.modelPeriods.endDate()))
        record.setValue('duration', toVariant(fullLength))
        if (self.prolonging or forceInt(record.value('closed')) == 2) and (not self.saveProlonging):
            closed = 2
        else:
            closed = self.modelPeriods.getTempInvalidClosedStatus()
        record.setValue('closed', toVariant(closed))
        date = self.modelPeriods.endDate()
        if not date:
            date = self.modelPeriods.begDate()
        getLineEditValue(self.edtMainNumber, record, 'mainNumber')

        diagnosis = getDiagnosisId2(
            date,
            self.modelPeriods.lastPerson(),
            self.clientId,
            1,  # diagnosisType = закл
            self.edtDiagnosis.text(),
            u'',
            self.cmbDiseaseCharacter.value(),
            None,
            None
        )
        self.diagnosisId = diagnosis[0]
        record.setValue('diagnosis_id', toVariant(diagnosis[0]))

        record.setValue('person_id', toVariant(self.modelPeriods.lastPerson()))
        record.setValue('prev_id', toVariant(self.prevId))
        if not self.caseBegDate:
            self.caseBegDate = self.modelPeriods.begDate()
        record.setValue('caseBegDate', toVariant(self.caseBegDate))
        if self.saveProlonging:
            recordTempInvalid = tableTempInvalid.newRecord()
            recordTempInvalid.setValue('type', toVariant(self.type_))
            recordTempInvalid.setValue('client_id', toVariant(self.clientId))
            tempInvalidId = db.insertOrUpdate(tableTempInvalid, recordTempInvalid)
            record.setValue('id', toVariant(tempInvalidId))
            self.modelPeriods.saveItems(tempInvalidId)
            self.saveProlonging = False
        else:
            self.modelPeriods.saveItems(itemId)

        if not self.defaultBlankMovingId:
            blankMovingId = None
        else:
            blankMovingId = self.defaultBlankMovingId
        if blankMovingId:
            recordMoving = db.getRecordEx(
                tableBTIMoving, u'*', [tableBTIMoving['deleted'].eq(0), tableBTIMoving['id'].eq(blankMovingId)]
            )
            if recordMoving:
                used = forceInt(recordMoving.value('used'))
                recordMoving.setValue('used', toVariant(used + 1))
                db.updateRecord(tableBTIMoving, recordMoving)
        return record

    def exec_(self):
        if self.lock(self._tableName, self._id):
            try:
                result = CDialogBase.exec_(self)
                if not result:
                    self.onCancelButtonBox()
            finally:
                self.releaseLock()
        else:
            result = QtGui.QDialog.Rejected
            self.setResult(result)
        return result

    def onCancelButtonBox(self):
        if self.saveProlonging:
            itemId = self.itemId()
            if itemId:
                db = QtGui.qApp.db
                table = db.table('TempInvalid')
                db.updateRecords(
                    table.name(), table['closed'].eq(self.closed), [table['deleted'].eq(0), table['id'].eq(itemId)]
                )

    def checkDataEntered(self):
        result = True
        doctype = self.cmbDoctype.currentIndex()
        reasonId = self.cmbReason.value()

        result = result and (reasonId or self.checkInputMessage(u'причину', False, self.cmbReason))
        result = result \
                 and (forceStringEx(self.edtNumber.text()) or self.checkInputMessage(u'номер', True, self.edtNumber))

        # i4725@0019089: hide useless elements
        # if requiredOtherPerson(reasonId):
        #     result = result and (self.cmbOtherSex.currentIndex() or self.checkInputMessage(u'пол', False, self.cmbOtherSex))
        #     result = result and (self.edtOtherAge.value() or self.checkInputMessage(u'возраст', False, self.edtOtherAge))

        db = QtGui.qApp.db
        table = db.table('TempInvalid')

        # проверка на 2 или более листов трудоспособности у пациента за период
        cond = [
            table['client_id'].eq(self.clientId),
            table['deleted'].eq(0),
            table['endDate'].eq('0000-00-00')
        ]
        stmt = 'SELECT ' + db.existsStmt(table, cond)
        query = db.query(stmt)
        if query.first():
            anotherClientTempInvalid = forceBool(query.record().value(0))
            if anotherClientTempInvalid:
                return self.checkValueMessage(
                    u'Этот пациент уже имееть незакрытый листок ВУТ', False, self.tblPeriods, 0, 0
                )
        items = self.modelPeriods.items()
        result = result and (len(items) or self.checkInputMessage(u'период', False, self.tblPeriods, 0, 0))

        # проверка правильности диагноза
        MKB = self.edtDiagnosis.text()

        if requiredDiagnosis(self.cmbReason.value()):
            if not MKB:
                self.checkInputMessage(u'диагноз', False, self.edtDiagnosis, 0, 0)
                return

        date = None
        for row, record in enumerate(items):
            date, recordOk = self.checkPeriodDataEntered(date, row, record)
            if not recordOk:
                return False

        # проверка отсутствия пересекающихся периодов нетрудоспособности, если не совместитель
        if self.cmbBusyness.value() != Busyness.Combine:
            begDate = self.modelPeriods.begDate()
            endDate = self.modelPeriods.endDate()

            cond = [
                table['begDate'].between(begDate, endDate),
                table['endDate'].between(begDate, endDate),
                db.joinAnd([table['begDate'].le(begDate), table['endDate'].ge(begDate)]),
                db.joinAnd([table['begDate'].le(endDate), table['endDate'].ge(endDate)]),
            ]
            cond = [db.joinOr(cond)]
            cond.append(table['id'].ne(self.itemId()))
            cond.append(table['client_id'].eq(self.clientId))
            cond.append(table['deleted'].eq(0))
            cond.append(table['doctype_id'].eq(self.cmbDoctype.value()))

            stmt = 'SELECT ' + db.existsStmt(table, cond) + ' AS X'
            query = db.query(stmt)
            if query.first():
                present = forceBool(query.record().value(0))
                if present:
                    return self.checkValueMessage(
                        u'Период нетрудоспособности пересекается с существующим', False, self.tblPeriods, 0, 0
                    )

        # проверка корректности введённых дат нахождения в стационаре
        for it in self.modelPeriods.items():
            begDateHospital = forceDate(it.value('begDateHospital'))
            endDateHospital = forceDate(it.value('endDateHospital'))
            if begDateHospital.isValid() and not endDateHospital.isValid():
                return self.checkValueMessage(
                    u'Введена только дата поступления в стационар', False, self.tblPeriods, 0, 0
                )
            if not begDateHospital.isValid() and endDateHospital.isValid():
                return self.checkValueMessage(
                    u'Введена только дата выписки из стационара', False, self.tblPeriods, 0, 0
                )
            if (begDateHospital > endDateHospital):
                return self.checkValueMessage(
                    u'Дата поступления в стационар должна быть раньше даты выписки', False, self.tblPeriods, 0, 0
                )
        return result

    def checkPeriodDataEntered(self, prevPeriodEndDate, row, record):
        self.tblPeriods.model()
        model = self.tblPeriods.model()
        begDateIndex = model.getColIndex('begDate')
        endDateIndex = model.getColIndex('endDate')
        resultIndex = model.getColIndex('result_id')
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        resultId = forceRef(record.value('result_id'))
        result = True
        if result and (not begDate or begDate.isNull()):
            result = self.checkValueMessage(
                u'Не заполнена дата начала периода', False, self.tblPeriods, row, begDateIndex
            )
        if result and (prevPeriodEndDate and prevPeriodEndDate.daysTo(begDate) != 1):
            result = self.checkValueMessage(
                u'Недопустимая дата начала периода', False, self.tblPeriods, row, begDateIndex
            )
        if result and endDate and not endDate.isNull() and (begDate.daysTo(endDate) < 0):
            result = self.checkValueMessage(
                u'Недопустимая дата окончания периода', False, self.tblPeriods, row, endDateIndex
            )
        if result and (not resultId):
            result = self.checkValueMessage(
                u'Не заполнен результат периода', False, self.tblPeriods, row, resultIndex
            )
        return endDate, result

    def checkBlankSerialNumberAmount(self):
        pass
        # self.defaultBlankMovingId = None
        # result = True
        # blankMovingId = self.edtSerial.value()
        # serial = forceString(self.edtSerial.text())
        # number = forceInt(toVariant(self.edtNumber.text()))
        # if blankMovingId:
        #     blankInfo = self.blankParams.get(blankMovingId, {})
        #     if blankInfo:
        #         result = self.checkBlankParams(blankInfo, result, serial, blankMovingId, number)
        # elif serial:
        #     for movingId, blankInfo in self.blankParams.items():
        #         serialCache = forceString(blankInfo.get('serial', u''))
        #         if serial == serialCache:
        #             result = self.checkBlankParams(blankInfo, result, serial, movingId, number)
        #             if result:
        #                 self.defaultBlankMovingId = movingId
        #             return result
        # return result

    def checkBlankParams(self, blankInfo, result, serial, blankMovingId, number):
        db = QtGui.qApp.db
        tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
        checkingSerialCache = forceInt(toVariant(blankInfo.get('checkingSerial', 0)))
        serialCache = forceString(blankInfo.get('serial', u''))
        # if checkingSerialCache:
        #     result = result and (serialCache == serial or self.checkValueMessage(u'Серия не соответсвует документу', True if checkingSerialCache == 1 else False, self.edtSerial))
        if result:
            checkingNumberCache = forceInt(toVariant(blankInfo.get('checkingNumber', 0)))
            if checkingNumberCache:
                numberFromCache = forceInt(toVariant(blankInfo.get('numberFrom', u'')))
                numberToCache = forceInt(toVariant(blankInfo.get('numberTo', u'')))
                result = result and ((number >= numberFromCache and  number <= numberToCache) or self.checkValueMessage(u'Номер не соответсвует диапазону номеров документа', True if checkingNumberCache == 1 else False, self.edtNumber))
        if result:
            checkingAmountCache = forceInt(toVariant(blankInfo.get('checkingAmount', 0)))
            if checkingAmountCache:
                record = db.getRecordEx(tableBlankTempInvalidMoving, [tableBlankTempInvalidMoving['returnAmount'], tableBlankTempInvalidMoving['used'], tableBlankTempInvalidMoving['received']], [tableBlankTempInvalidMoving['deleted'].eq(0), tableBlankTempInvalidMoving['id'].eq(blankMovingId)])
                returnAmount = forceInt(record.value('returnAmount'))
                used = forceInt(record.value('used'))
                received = forceInt(record.value('received'))
                balance = received - used - returnAmount
                # result = result and (balance > 0 or self.checkValueMessage(u'В партии закончились соответствующие документы', True if checkingAmountCache == 1 else False, self.edtSerial))
        return result

    def updateLength(self):
        fullLength, externalLength = self.modelPeriods.calcLengths()
        self.lblLengthValue.setText(str(fullLength))
        self.lblExternalLengthValue.setText(str(externalLength))
        if self.caseBegDate:
            caseLength = self.caseBegDate.daysTo(self.modelPeriods.begDate())+fullLength
        else:
            caseLength = fullLength
        self.lblCaseLengthValue.setText(str(caseLength))

    def newTempInvalid(self, begDate):
        self.tempInvalidId = None
        self.insuranceOfficeMark = None
        self.btnTempInvalidProlong.setEnabled(not self.prolonging)
        self.prolonging = False
        self.modelPeriods.clearItems()
        self.modelPeriods.addStart(begDate)
        self.edtNumber.setText('')
        self.chkInsuranceOfficeMark.setChecked(False)
        self.updateLength()

    def getMKBs(self):
        if self.diagnosisId:
            db = QtGui.qApp.db
            record = db.getRecord('Diagnosis', 'MKB, MKBEx', self.diagnosisId)
            if record:
               return forceString(record.value('MKB')), forceString(record.value('MKBEx'))
        return '', ''

    def getTempInvalidInfo(self, context):
        result = context.getInstance(CTempInvalidInfo, None)
        result._doctype = context.getInstance(CTempInvalidDocTypeInfo,  self.cmbDoctype.value())
        result._reason  = context.getInstance(CTempInvalidReasonInfo,  self.cmbReason.value())
        result._extraReason  = context.getInstance(CTempInvalidExtraReasonInfo, forceRef(self.cmbExtraReason.value()))
        result._busyness = forceInt(self.cmbBusyness.value())
        result._placeWork = forceString(self.edtPlaceWork.text())
        result._number  = forceStringEx(self.edtNumber.text())
        result._sex     = formatSex(self.cmbOtherSex.currentIndex())
        result._age     = self.edtOtherAge.value()
        result._duration, result._externalDuration = self.modelPeriods.calcLengths()
        result._begDate = CDateInfo(self.modelPeriods.begDate())
        result._endDate = CDateInfo(self.modelPeriods.endDate())
        MKB, MKBEx = self.getMKBs()
        result._MKB = context.getInstance(CMKBInfo, MKB)
        result._MKBEx = context.getInstance(CMKBInfo, MKBEx)
        closed = self.modelPeriods.getTempInvalidClosedStatus()
        result._closed = closed
        result._periods = self.modelPeriods.getPeriodsInfo(context)
        if self.prevId:
            result._prev = context.getInstance(CTempInvalidInfo, self.prevId)
        else:
            result._prev = None
        result._ok = True
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbDoctype_currentIndexChanged(self, index):
        self.getBlankParams()

    @QtCore.pyqtSlot(int)
    def on_cmbReason_currentIndexChanged(self, index):
        self.setEnabledWidget(self.chkInsuranceOfficeMark.isChecked(), [self.cmbDoctype, self.cmbReason, self.cmbExtraReason, self.edtNumber, self.edtDiagnosis, self.cmbDiseaseCharacter, self.chkInsuranceOfficeMark, self.tblPeriods])

    @QtCore.pyqtSlot()
    def on_btnTempInvalidProlong_clicked(self):
        if not self.checkDataEntered():
            return

        self.prolonging = True
        if not self.save():
            self.prolonging = False
            self.saveProlonging = False
            return
        self.saveProlonging = True
        itemId = self.itemId()
        if itemId:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            prevRecord = db.getRecordEx(table, '*', [table['id'].eq(itemId), table['deleted'].eq(0), table['client_id'].eq(self.clientId), table['type'].eq(self.type_), table['closed'].eq(2)], 'endDate DESC')
            self.setPrev(prevRecord)
        self.newTempInvalid(forceDate(self.modelPeriods.endDate().addDays(1)))
        self.tblPeriods.setFocus(QtCore.Qt.OtherFocusReason)
        self.tblPeriods.setCurrentIndex(self.modelPeriods.index(0, 1))

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        from Registry.RegistryWindow import getEventInfoByDiagnosis
        context = CInfoContext()
        tempInvalidInfo = self.getTempInvalidInfo(context)
        eventInfo = getEventInfoByDiagnosis(context, self.diagnosisId)
        data = { 'event' : eventInfo,
                 'client': context.getInstance(CClientInfo, self.clientId, QtCore.QDate.currentDate()),
                 'tempInvalid': tempInvalidInfo,
               }
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot()
    def on_btnNewLN_clicked(self):
        if forceString(QtGui.qApp.preferences.appPrefs['LNService']) \
                and forceString(QtGui.qApp.preferences.appPrefs['LNAddress']):
            ex = LnService()
            number = ex.getNewLnNumber()
            if number:
                self.edtNumber.setText(number)
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Сервис листов нетрудоспособности не настроен.')

    @QtCore.pyqtSlot()
    def on_btnSendInFSS_clicked(self):
        self.getRecord()
        ex = LnService()
        if forceString(self.edtNumber.text()):
            if ex.prParseFilelnlpu(self.edtNumber.text()):
                QtGui.QMessageBox.information(self, u'Успешно', u'Лист нетрудоспособности успешно отправлен')
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не заполнен номер листа нетрудоспособности')
            return

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelPeriods_dataChanged(self, topLeft, bottomRight):
        self.updateLength()
        closed = self.modelPeriods.getTempInvalidClosedStatus()
        self.btnTempInvalidProlong.setEnabled(closed == 0 and self.closed != 2)

    @QtCore.pyqtSlot(int)
    def on_cmbBusyness_currentIndexChanged(self, index):
        isCombine = self.cmbBusyness.value() == Busyness.Combine
        if not isCombine:
            self.edtMainNumber.clear()
        self.lblMainNumber.setEnabled(isCombine)
        self.edtMainNumber.setEnabled(isCombine)

    def getDiagFilter(self):
        db =QtGui.qApp.db
        specialityId = forceRef(db.translate('Person', 'id', self.modelPeriods.lastPerson(), 'speciality_id'))
        result = self.mapSpecialityIdToDiagFilter.get(specialityId, None)
        if result is None:
            result = db.translate('rbSpeciality', 'id', specialityId, 'mkbFilter')
            if result is None:
                result = ''
            else:
                result = forceString(result)
            self.mapSpecialityIdToDiagFilter[specialityId] = forceString(result)
        return result

    def setEditorDataTI(self):
        db = QtGui.qApp.db
        MKB  = self.edtDiagnosis.text()
        codeIdList = getAvailableCharacterIdByMKB(MKB)
        table = db.table('rbDiseaseCharacter')
        self.cmbDiseaseCharacter.setTable(table.name(), not bool(codeIdList), filter=table['id'].inlist(codeIdList))

    def updateCharacterByMKB(self, MKB, specifiedCharacterId):
        characterIdList = getAvailableCharacterIdByMKB(MKB)
        if specifiedCharacterId in characterIdList:
            characterId = specifiedCharacterId
        else:
            characterId = forceRef(self.cmbDiseaseCharacter.value())
            if (characterId in characterIdList) or (characterId is None and not characterIdList) :
                return
            if characterIdList:
                characterId = characterIdList[0]
            else:
                characterId = None
        self.cmbDiseaseCharacter.setValue(characterId)

    def specifyDiagnosis(self, MKB):
        diagFilter = self.getDiagFilter()
        date = self.modelPeriods.begDate()
        if not date:
            date = QtCore.QDate.currentDate()
        acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId, modifiableDiagnosisId = specifyDiagnosis(self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, date)
        self.modifiableDiagnosisesMap[specifiedMKB] = modifiableDiagnosisId
        return acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId


class CTempInvalidCreateDialog(CTempInvalidEditDialog):
    def __init__(self,  parent, clientId = None):
        CTempInvalidEditDialog.__init__(self, parent)
        self.lblDiagnosis.setVisible(True)
        self.edtDiagnosis.setVisible(True)
        self.lblDiseaseCharacter.setVisible(True)
        self.cmbDiseaseCharacter.setVisible(True)
        self.clientId = clientId
        self.clientSex = None
        self.clientAge = None
        self.modifiableDiagnosisesMap = {}
        self.mapSpecialityIdToDiagFilter = {}
        self.cmbDiseaseCharacter.setTable('rbDiseaseCharacter', order='code')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('type', toVariant(self.type_))
        getRBComboBoxValue(self.cmbDoctype, record, 'doctype_id')
        record.setValue('client_id', toVariant(self.clientId))
        getRBComboBoxValue(self.cmbReason,  record, 'tempInvalidReason_id')
        getRBComboBoxValue(self.cmbExtraReason,  record, 'tempInvalidExtraReason_id')
        getWidgetValue(self.cmbBusyness, record, 'busyness')
        getLineEditValue(self.edtPlaceWork, record, 'placeWork')
        # getLineEditValue(self.edtSerial,    record, 'serial')
        getLineEditValue(self.edtNumber,    record, 'number')
        getComboBoxValue(self.cmbOtherSex,  record, 'sex')
        getSpinBoxValue(self.edtOtherAge,   record, 'age')
        getCheckBoxValue(self.chkInsuranceOfficeMark,  record, 'insuranceOfficeMark')
        getLineEditValue(self.edtMainNumber, record, 'mainNumber')
        fullLength, externalLength = self.modelPeriods.calcLengths()
        record.setValue('begDate',  toVariant(self.modelPeriods.begDate()))
        record.setValue('endDate',  toVariant(self.modelPeriods.endDate()))
        record.setValue('duration', toVariant(fullLength))
        date = self.modelPeriods.endDate()
        if not date:
            date = self.modelPeriods.begDate()
        diagnosisTypeId = 1 #diagnosisType = закл
        diagnosis = getDiagnosisId2(date, self.modelPeriods.lastPerson(), self.clientId, diagnosisTypeId, self.edtDiagnosis.text(), u'', self.cmbDiseaseCharacter.value(), None, None)
        record.setValue('diagnosis_id', toVariant(diagnosis[0]))
        if (self.prolonging or forceInt(record.value('closed')) == 2) and (not self.saveProlonging):
            closed = 2
        else:
            closed = self.modelPeriods.getTempInvalidClosedStatus()
        #self.closed = closed
        record.setValue('closed',   toVariant(closed))
        record.setValue('prev_id', toVariant(self.prevId))
        record.setValue('person_id', toVariant(self.modelPeriods.lastPerson()))
        if not self.caseBegDate:
            self.caseBegDate = self.modelPeriods.begDate()
        record.setValue('caseBegDate', toVariant(self.caseBegDate))
        db = QtGui.qApp.db
        table = db.table('TempInvalid')
        tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
        if not self.defaultBlankMovingId:
            blankMovingId = None
        else:
            blankMovingId = self.defaultBlankMovingId
        if blankMovingId:
            recordMoving = db.getRecordEx(tableBlankTempInvalidMoving, u'*', [tableBlankTempInvalidMoving['deleted'].eq(0), tableBlankTempInvalidMoving['id'].eq(blankMovingId)])
            used = forceInt(recordMoving.value('used'))
            recordMoving.setValue('used', toVariant(used + 1))
            db.updateRecord(tableBlankTempInvalidMoving, recordMoving)
        if self.saveProlonging:
            recordTempInvalid = table.newRecord()
            recordTempInvalid.setValue('type', toVariant(self.type_))
            recordTempInvalid.setValue('client_id', toVariant(self.clientId))
            tempInvalidId = db.insertOrUpdate(table, recordTempInvalid)
            record.setValue('id', toVariant(tempInvalidId))
            self.modelPeriods.saveItems(tempInvalidId)
            self.saveProlonging = False
        else:
            self.tempInvalidId = db.insertOrUpdate(table, record)
            record.setValue('id', toVariant(self.tempInvalidId))
            self.modelPeriods.saveItems(self.tempInvalidId)
        return record

    def getMKBs(self):
        return unicode(self.edtDiagnosis.text()), ''

    def getDiagFilter(self):
        db =QtGui.qApp.db
        specialityId = forceRef(db.translate('Person', 'id', self.modelPeriods.lastPerson(), 'speciality_id'))
        result = self.mapSpecialityIdToDiagFilter.get(specialityId, None)
        if result is None:
            result = db.translate('rbSpeciality', 'id', specialityId, 'mkbFilter')
            if result is None:
                result = ''
            else:
                result = forceString(result)
            self.mapSpecialityIdToDiagFilter[specialityId] = forceString(result)
        return result

    def specifyDiagnosis(self, MKB):
        diagFilter = self.getDiagFilter()
        date = self.modelPeriods.begDate()
        if not date:
            date = QtCore.QDate.currentDate()
        acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId, modifiableDiagnosisId = specifyDiagnosis(self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, date)
        self.modifiableDiagnosisesMap[specifiedMKB] = modifiableDiagnosisId
        return acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId

    def setEditorDataTI(self):
        db = QtGui.qApp.db
        MKB  = self.edtDiagnosis.text()
        codeIdList = getAvailableCharacterIdByMKB(MKB)
        table = db.table('rbDiseaseCharacter')
        self.cmbDiseaseCharacter.setTable(table.name(), not bool(codeIdList), filter=table['id'].inlist(codeIdList))

    def updateCharacterByMKB(self, MKB, specifiedCharacterId):
        characterIdList = getAvailableCharacterIdByMKB(MKB)
        if specifiedCharacterId in characterIdList:
            characterId = specifiedCharacterId
        else:
            characterId = forceRef(self.cmbDiseaseCharacter.value())
            if (characterId in characterIdList) or (characterId is None and not characterIdList) :
                return
            if characterIdList:
                characterId = characterIdList[0]
            else:
                characterId = None
        self.cmbDiseaseCharacter.setValue(characterId)
