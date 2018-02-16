# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.interchange        import getCheckBoxValue, getDateEditValue, getLineEditValue, getRBComboBoxValue, \
                                       getTextEditValue, setCheckBoxValue, setDateEditValue, setLineEditValue, \
                                       setRBComboBoxValue, setTextEditValue
from library.ItemsListDialog    import CItemEditorBaseDialog
from library.Utils              import forceInt, forceRef, forceString, forceStringEx, toVariant

from Users.Rights               import urRegWriteInsurOfficeMark

from Ui_TempInvalidDuplicateEditDialog import Ui_TempInvalidDuplicateEditDialog


class CTempInvalidDuplicateEditDialog(CItemEditorBaseDialog, Ui_TempInvalidDuplicateEditDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'TempInvalidDuplicate')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Дубликат документа временной нетрудоспособности')
        self.cmbReason.setTable('rbTempInvalidDuplicateReason')
        self.edtDate.setDate(QtCore.QDate.currentDate())
        if QtGui.qApp.userSpecialityId:
            self.cmbPerson.setValue(QtGui.qApp.userId)
        self.tempInvalidId = None
        self.defaultBlankMovingId = None
        self.blankParams = {}
        self.setupDirtyCather()
        self.chkInsuranceOfficeMark.setEnabled(QtGui.qApp.userHasRight(urRegWriteInsurOfficeMark))


    @QtCore.pyqtSlot(int)
    def on_cmbReason_currentIndexChanged(self):
        self.edtPlaceWork.setEnabled(self.cmbReason.code() == '1')


    def setTempInvalid(self, tempInvalidId):
        self.tempInvalidId = tempInvalidId
        self.getBlankParams()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setCheckBoxValue(self.chkInsuranceOfficeMark, record, 'insuranceOfficeMark')
        self.setEnabledWidget(self.chkInsuranceOfficeMark.isChecked(), [self.edtDestination, self.edtDate, self.edtSerial, self.edtNumber, self.cmbReason, self.edtNote, self.chkInsuranceOfficeMark])
        setLineEditValue(self.edtSerial,       record, 'serial')
        setLineEditValue(self.edtNumber,       record, 'number')
        setDateEditValue(self.edtDate,         record, 'date')
        setRBComboBoxValue(self.cmbPerson,     record, 'person_id')
        setRBComboBoxValue(self.cmbExpert,     record, 'expert_id')
        setLineEditValue(self.edtDestination,  record, 'destination')
        setRBComboBoxValue(self.cmbReason,     record, 'reason_id')
        setTextEditValue(self.edtNote,         record, 'note')
        setLineEditValue(self.edtPlaceWork,    record, 'placeWork')
        self.edtPlaceWork.setEnabled(self.cmbReason.code() == '1')
        self.tempInvalidId = forceRef(record.value('tempInvalid_id'))
        self.getBlankParams()
        self.setIsDirty(False)
        self.defaultBlankMovingId = None


    def setEnabledWidget(self, checked, listWidget=None):
        if not listWidget:
            listWidget = []
        enabled = QtGui.qApp.userHasRight(urRegWriteInsurOfficeMark)
        if checked:
            for widget in listWidget:
                widget.setEnabled(enabled)
        else:
            self.chkInsuranceOfficeMark.setEnabled(enabled)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtSerial,       record, 'serial')
        getLineEditValue(self.edtNumber,       record, 'number')
        getDateEditValue(self.edtDate,         record, 'date')
        getRBComboBoxValue(self.cmbPerson,     record, 'person_id')
        getRBComboBoxValue(self.cmbExpert,     record, 'expert_id')
        getLineEditValue(self.edtDestination,  record, 'destination')
        getRBComboBoxValue(self.cmbReason,     record, 'reason_id')
        getTextEditValue(self.edtNote,         record, 'note')
        getCheckBoxValue(self.chkInsuranceOfficeMark, record, 'insuranceOfficeMark')
        record.setValue('tempInvalid_id', toVariant(self.tempInvalidId))
        getLineEditValue(self.edtPlaceWork,    record, 'placeWork')
        if not self.defaultBlankMovingId:
            blankMovingId = self.edtSerial.value()
        else:
            blankMovingId = self.defaultBlankMovingId
        if blankMovingId:
            db = QtGui.qApp.db
            tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
            recordMoving = db.getRecordEx(tableBlankTempInvalidMoving, u'*', [tableBlankTempInvalidMoving['deleted'].eq(0), tableBlankTempInvalidMoving['id'].eq(blankMovingId)])
            if recordMoving:
                used = forceInt(recordMoving.value('used'))
                recordMoving.setValue('used', toVariant(used + 1))
                db.updateRecord(tableBlankTempInvalidMoving, recordMoving)
        return record


    def checkDataEntered(self):
        result = True
        serial = forceStringEx(self.edtNumber.text())
        number = forceStringEx(self.edtNumber.text())
        result = result and (serial or self.checkInputMessage(u'серию', False, self.edtSerial))
        result = result and (number or self.checkInputMessage(u'номер', False, self.edtNumber))
        result = result and (self.edtDate.date() or self.checkInputMessage(u'дату выдачи', False, self.edtDate))
        result = result and (self.cmbPerson.value() or self.checkInputMessage(u'выдавшего врача', False, self.cmbPerson))
        if self.tempInvalidId:
            db = QtGui.qApp.db
            tableTempInvalid = db.table('TempInvalid')
            tableTempInvalidDuplicate = db.table('TempInvalidDuplicate')
            record = db.getRecordEx(tableTempInvalid, [tableTempInvalid['doctype_id']], [tableTempInvalid['id'].eq(self.tempInvalidId), tableTempInvalid['deleted'].eq(0)])
            if not record:
                return
            docTypeId = forceRef(record.value('doctype_id'))
            result = result and self.checkTempInvalidDuplicateSerialNumber(docTypeId)
            result = result and self.checkTempInvalidSerialNumber(docTypeId)
        result = result and self.checkBlankSerialNumberAmount()
        return result


    def checkTempInvalidDuplicateSerialNumber(self, docTypeId = None):
        result = True
        serial = self.edtSerial.text()
        number = self.edtNumber.text()
        if len(serial) > 0 or len(number) > 0:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            tableTempInvalidDuplicate = db.table('TempInvalidDuplicate')
            queryTable = tableTempInvalidDuplicate.innerJoin(table, table['id'].eq(tableTempInvalidDuplicate['tempInvalid_id']))
            cond =[table['doctype_id'].eq(docTypeId)]
            if len(serial) > 0:
                cond.append(tableTempInvalidDuplicate['serial'].eq(serial))
            if len(number) > 0:
                cond.append(tableTempInvalidDuplicate['number'].eq(number))
            recordNumber = db.getRecordEx(queryTable, 'TempInvalidDuplicate.id, TempInvalidDuplicate.serial, TempInvalidDuplicate.number', cond)
            if recordNumber:
                serialRecord = forceString(recordNumber.value('serial'))
                numberRecord = forceString(recordNumber.value('number'))
                if len(serialRecord) > 0 and len(numberRecord) > 0:
                    message = u'Серия и номер: %s %s, документа ВУТ не уникальны' % (serialRecord, numberRecord)
                elif len(serialRecord) > 0:
                    message = u'Серия: %s, документа ВУТ не уникальна' % (serialRecord)
                elif len(numberRecord) > 0:
                    message = u'Номер: %s, документа ВУТ не уникален' % (numberRecord)
                result = result and self.checkValueMessage(message, True, self.edtNumber)
        return result


    def checkTempInvalidSerialNumber(self, docTypeId = None):
        result = True
        serial = self.edtSerial.text()
        number = self.edtNumber.text()
        if len(serial) > 0 or len(number) > 0:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            cond =[table['doctype_id'].eq(docTypeId)]
            if len(serial) > 0:
                cond.append(table['serial'].eq(serial))
            if len(number) > 0:
                cond.append(table['number'].eq(number))
            recordNumber = db.getRecordEx(table, 'id, serial, number', cond)
            if recordNumber:
                serialRecord = forceString(recordNumber.value('serial'))
                numberRecord = forceString(recordNumber.value('number'))
                if len(serialRecord) > 0 and len(numberRecord) > 0:
                    message = u'Серия и номер: %s %s, документа ВУТ не уникальны' % (serialRecord, numberRecord)
                elif len(serialRecord) > 0:
                    message = u'Серия: %s, документа ВУТ не уникальна' % (serialRecord)
                elif len(numberRecord) > 0:
                    message = u'Номер: %s, документа ВУТ не уникален' % (numberRecord)

                result = result and self.checkValueMessage(message, True, self.edtNumber)
        return result


    def checkBlankSerialNumberAmount(self):
        self.defaultBlankMovingId = None
        result = True
        blankMovingId = self.edtSerial.value()
        serial = forceString(self.edtSerial.text())
        number = forceInt(toVariant(self.edtNumber.text()))
        if blankMovingId:
            blankInfo = self.blankParams.get(blankMovingId, {})
            if blankInfo:
                result = self.checkBlankParams(blankInfo, result, serial, blankMovingId, number)
        elif serial:
            for movingId, blankInfo in self.blankParams.items():
                serialCache = forceString(blankInfo.get('serial', u''))
                if serial == serialCache:
                    result = self.checkBlankParams(blankInfo, result, serial, movingId, number)
                    if result:
                        self.defaultBlankMovingId = movingId
                    return result
        return result


    def checkBlankParams(self, blankInfo, result, serial, blankMovingId, number):
        db = QtGui.qApp.db
        tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
        checkingSerialCache = forceInt(toVariant(blankInfo.get('checkingSerial', 0)))
        serialCache = forceString(blankInfo.get('serial', u''))
        if checkingSerialCache:
            result = result and (serialCache == serial or self.checkValueMessage(u'Серия не соответсвует документу', True if checkingSerialCache == 1 else False, self.edtSerial))
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
                result = result and (balance > 0 or self.checkValueMessage(u'В партии закончились соответствующие документы', True if checkingAmountCache == 1 else False, self.edtSerial))
        return result


    def getBlankParams(self):
        self.defaultBlankMovingId = None
        self.blankParams = {}
        blankIdList = []
        if self.tempInvalidId:
            db = QtGui.qApp.db
            tableTempInvalid = db.table('TempInvalid')
            record = db.getRecordEx(tableTempInvalid, [tableTempInvalid['doctype_id']], [tableTempInvalid['id'].eq(self.tempInvalidId), tableTempInvalid['deleted'].eq(0)])
            if not record:
                return
            docTypeId = forceRef(record.value('doctype_id'))
            if docTypeId:
                tableTempInvalidDuplicate = db.table('TempInvalidDuplicate')
                tableRBBlankTempInvalids = db.table('rbBlankTempInvalids')
                tableBlankTempInvalidParty = db.table('BlankTempInvalid_Party')
                tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
                tablePerson = db.table('Person')
                orgStructureId = None
                date = QtCore.QDate.currentDate()
                personId = QtGui.qApp.userId
                if personId:
                    orgStructRecord = db.getRecordEx(tablePerson, [tablePerson['orgStructure_id']], [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId)])
                    orgStructureId = forceRef(orgStructRecord.value('orgStructure_id')) if orgStructRecord else None
                cols = [tableBlankTempInvalidMoving['id'].alias('blankMovingId'),
                        tableRBBlankTempInvalids['checkingSerial'],
                        tableRBBlankTempInvalids['checkingNumber'],
                        tableRBBlankTempInvalids['checkingAmount'],
                        tableBlankTempInvalidParty['serial'],
                        tableBlankTempInvalidMoving['numberFrom'],
                        tableBlankTempInvalidMoving['numberTo'],
                        tableBlankTempInvalidMoving['returnAmount'],
                        tableBlankTempInvalidMoving['used'],
                        tableBlankTempInvalidMoving['received']
                        ]
                cond = [tableRBBlankTempInvalids['doctype_id'].eq(docTypeId),
                        tableBlankTempInvalidParty['deleted'].eq(0),
                        tableBlankTempInvalidMoving['deleted'].eq(0)
                        ]
                order = []
                if date:
                    cond.append(tableBlankTempInvalidMoving['date'].le(date))
                orgStructureIdList = db.getTheseAndParents('OrgStructure', 'parent_id', [orgStructureId]) if orgStructureId else []
                if personId and orgStructureIdList:
                    cond.append(db.joinOr([tableBlankTempInvalidMoving['person_id'].eq(personId), tableBlankTempInvalidMoving['orgStructure_id'].inlist(orgStructureIdList)]))
                    order.append(u'BlankTempInvalid_Moving.person_id')
                elif personId:
                    cond.append(tableBlankTempInvalidMoving['person_id'].eq(personId))
                elif orgStructureIdList:
                    cond.append(tableBlankTempInvalidMoving['orgStructure_id'].inlist(orgStructureIdList))
                queryTable = tableRBBlankTempInvalids.innerJoin(tableBlankTempInvalidParty, tableBlankTempInvalidParty['doctype_id'].eq(tableRBBlankTempInvalids['id']))
                queryTable = queryTable.innerJoin(tableBlankTempInvalidMoving, tableBlankTempInvalidMoving['blankParty_id'].eq(tableBlankTempInvalidParty['id']))
                order.append(u'rbBlankTempInvalids.checkingSerial, rbBlankTempInvalids.checkingNumber, rbBlankTempInvalids.checkingAmount DESC')
                records = db.getRecordList(queryTable, cols, cond, order)
                for record in records:
                    blankInfo = {}
                    blankMovingId = forceRef(record.value('blankMovingId'))
                    checkingSerial = forceInt(record.value('checkingSerial'))
                    checkingNumber = forceInt(record.value('checkingNumber'))
                    checkingAmount = forceInt(record.value('checkingAmount'))
                    serial = forceString(record.value('serial'))
                    numberFrom = forceInt(record.value('numberFrom'))
                    numberTo = forceInt(record.value('numberTo'))
                    returnAmount = forceInt(record.value('returnAmount'))
                    used = forceInt(record.value('used'))
                    received = forceInt(record.value('received'))
                    blankInfo['checkingSerial'] = checkingSerial
                    blankInfo['checkingNumber'] = checkingNumber
                    blankInfo['checkingAmount'] = checkingAmount
                    blankInfo['serial'] = serial
                    blankInfo['numberFrom'] = numberFrom
                    blankInfo['numberTo'] = numberTo
                    blankInfo['returnAmount'] = returnAmount
                    blankInfo['used'] = used
                    blankInfo['received'] = received
                    self.blankParams[blankMovingId] = blankInfo
                    blankIdList.append(blankMovingId)
            self.edtSerial.setTempInvalidBlankIdList(blankIdList)
            if self.edtSerial.blankIdList:
                movingId = self.edtSerial.blankIdList[0]
            else:
                movingId = None
            self.edtSerial.setValue(movingId)
            if movingId:
                blankInfo = self.blankParams.get(movingId, None)
                if blankInfo:
                    serial = forceString(blankInfo.get('serial', u''))
                    numberFrom = blankInfo.get('numberFrom', 0)
                    numberTo = blankInfo.get('numberTo', 0)
                    returnAmount = forceInt(blankInfo.get('returnAmount', 0))
                    used = forceInt(blankInfo.get('used', 0))
                    received = forceInt(blankInfo.get('received', 0))
                    balance = received - used - returnAmount
                    if balance > 0:
                        number = numberFrom + used + returnAmount + 1
                        if number <= numberTo:
                            record = db.getRecordEx(tableTempInvalid, [tableTempInvalid['id']], [tableTempInvalid['deleted'].eq(0), tableTempInvalid['serial'].eq(serial), tableTempInvalid['number'].eq(number)])
                            if not record:
                                self.edtNumber.setText(forceString(number))

