# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QDateTime, QTime, QString
from Events.Ui_RecipeEditDialog import Ui_RecipeEditDialog

from library.DialogBase          import CDialogBase

from library.PrintInfo import CInfoContext
from library.Recipe.RecipeInfo import CDloDrugFormularyItemInfo
from library.Recipe.Utils import checkDiagnosis, getBookkeeperCode, CRecipeStatusModel
from library.Utils import forceString, forceInt, forceRef, toVariant, forceDateTime, forceDate
from library.crbcombobox import CRBComboBox
from library.interchange import setComboBoxValue, setLineEditValue, setRBComboBoxValue, getRBComboBoxValue, getLineEditValue, getComboBoxValue, \
    setSpinBoxValue, getSpinBoxValue


class CRecipeEditDialog(CDialogBase, Ui_RecipeEditDialog):
    def __init__(self, parent, socStatuses, clientId, personId):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbSocCodes.blockSignals(True)
        for socStatus in socStatuses:
            if 'benefits' in [cl.flatCode for cl in socStatus.classes]:
                self.cmbSocCodes.addItem(socStatus.name, socStatus.code)
        self.cmbSocCodes.blockSignals(False)
        self.cmbFinance.setTable('rbFinance', True, 'code IN (70,71,72,73)')
        self.cmbFinance.setShowFields(CRBComboBox.showCodeAndName)
        self.personId = personId
        self.clientId = clientId

        self.addModels('RecipeStatus', CRecipeStatusModel())
        self.cmbStatus.setModel(self.modelRecipeStatus)

        db = QtGui.qApp.db
        self.drugMasterId = None
        record = db.getRecordEx(db.table('DloDrugFormulary'), [ 'id' ], 'type = 0 AND isActive = 1 AND deleted = 0')
        if record:
            self.drugMasterId = forceInt(record.value('id'))
            formularyFilter = 'master_id = %d AND isSprPC = 1' % self.drugMasterId
            self.cmbDrug.setTable('DloDrugFormulary_Item', True, filter=formularyFilter, order='`name` ASC')
        self.cmbDrug.setShowFields(CRBComboBox.showCodeAndName)
        self.cmbTerm.setCurrentIndex(2)
        self.rbtnVkNo.setChecked(True)
        self.rbtn100proc.setChecked(True)
        self.rbtnPrintMNN.setChecked(True)

        pregCardId = forceRef(db.translate('rbAccountingSystem', 'code', u'БЕРЕМ', 'id'))
        if pregCardId:
            record = db.getRecordEx(db.table('ClientIdentification'), [ 'identifier' ],
                                    'client_id = %d AND accountingSystem_id = %d AND deleted = 0' % (clientId, pregCardId))
            if record:
                self.edtPregCard.setText(forceString(record.value('identifier')))

        self.connect(self.cmbDrug, QtCore.SIGNAL('currentIndexChanged(int)'), self.drugSelected)
        self.connect(self.edtDosage, QtCore.SIGNAL('editingFinished()'), self.updateSigna)
        self.connect(self.spbQnt, QtCore.SIGNAL('valueChanged(int)'), self.updateSigna)
        self.connect(self.spbNumPerDay, QtCore.SIGNAL('valueChanged(int)'), self.updateSigna)
        self.connect(self.spbDuration, QtCore.SIGNAL('valueChanged(int)'), self.updateSigna)
        self.setMinimumWidth(min(self.parent().width(), 1000))

    def setRecord(self, record):
        annoyingWidgets = [self.cmbDrug, self.edtDosage, self.spbQnt, self.spbNumPerDay, self.spbDuration, self.cmbSocCodes]
        for widget in annoyingWidgets:
            widget.blockSignals(True)

        # self.disconnect(self.cmbDrug, QtCore.SIGNAL('currentIndexChanged(int)'), self.drugSelected)
        self.edtDate.setDate(forceDateTime(record.value('dateTime')).date())
        socCode = forceString(record.value('socCode'))
        i = self.cmbSocCodes.findData(socCode)
        self.cmbSocCodes.setCurrentIndex(i)
        pregCard = forceInt(record.value('pregCard'))
        if pregCard > 0:
            self.edtPregCard.setText(QString.number(pregCard))

        #mdldml: см. i2446
        financeId = forceRef(record.value('finance_id'))
        self.cmbFinance.setValue(financeId)
        if financeId:
            db = QtGui.qApp.db
            counterRecord = db.getRecordEx('rbCounter', '`id`', "`code`='%s'" % getBookkeeperCode(self.personId))
            if not counterRecord:
                self.cmbFinance.setEnabled(False)

        self.cmbMKB.setText(forceString(record.value('mkb')))
        setLineEditValue(self.edtDosage, record, 'dosage')
        setSpinBoxValue(self.spbQnt, record, 'qnt')
        setLineEditValue(self.edtSigna, record, 'signa')
        setSpinBoxValue(self.spbDuration, record, 'duration')
        setSpinBoxValue(self.spbNumPerDay, record, 'numPerDay')

        formularyFilter = 'master_id = %d AND isSprPC = 1' % forceInt(self.drugMasterId)
        if forceInt(record.value('isVk')) == 1:
            self.rbtnVkYes.setChecked(True)
        else:
            self.rbtnVkNo.setChecked(True)
            formularyFilter += ' AND federalCode IS NOT NULL'

        if forceInt(record.value('printMnn')) == 1:
            self.rbtnPrintMNN.setChecked(True)
        else:
            self.rbtnPrintTradeName.setChecked(True)

        self.cmbDrug.setFilter(formularyFilter, order='`name` ASC')
        setRBComboBoxValue(self.cmbDrug, record, 'formularyItem_id')
        context = CInfoContext()
        formularyItem = context.getInstance(CDloDrugFormularyItemInfo, forceRef(record.value('formularyItem_id')))
        self.rbtnPrintMNN.setEnabled(not formularyItem.mnn.code == u'1')

        if forceInt(record.value('percentage')) == 50:
            self.rbtn50proc.setChecked(True)
        else:
            self.rbtn100proc.setChecked(True)

        setComboBoxValue(self.cmbTerm, record, 'term')
        self.cmbStatus.setCurrentIndex(self.modelRecipeStatus.getIndex(forceInt(record.value('status'))))

        # self.connect(self.cmbDrug, QtCore.SIGNAL('currentIndexChanged(int)'), self.drugSelected)
        for widget in annoyingWidgets:
            widget.blockSignals(False)

    def getRecord(self, record):
        dateTime = QDateTime(self.edtDate.date(), QTime().currentTime())
        record.setValue('dateTime', dateTime)
        i = self.cmbSocCodes.currentIndex()
        socCode = forceString(self.cmbSocCodes.itemData(i))
        record.setValue('socCode', socCode)
        pregCard = forceInt(self.edtPregCard.text())
        if pregCard > 0:
            record.setValue('pregCard', pregCard)
        else:
            record.setNull('pregCard')
        getRBComboBoxValue(self.cmbFinance, record, 'finance_id')
        record.setValue('mkb', toVariant(self.cmbMKB.text()))
        getRBComboBoxValue(self.cmbDrug, record, 'formularyItem_id')
        getLineEditValue(self.edtDosage, record, 'dosage')
        getSpinBoxValue(self.spbQnt, record, 'qnt')
        getLineEditValue(self.edtSigna, record, 'signa')
        getSpinBoxValue(self.spbDuration, record, 'duration')
        getSpinBoxValue(self.spbNumPerDay, record, 'numPerDay')
        record.setValue('isVk', int(self.rbtnVkYes.isChecked()))
        record.setValue('printMnn', int(self.rbtnPrintMNN.isChecked()))
        record.setValue('percentage', int(50 if self.rbtn50proc.isChecked() else 100))
        getComboBoxValue(self.cmbTerm, record, 'term')
        record.setValue('status', self.modelRecipeStatus.getCode(self.cmbStatus.currentIndex()))
        record.setValue('deleted', 0)

    def checkDataEntered(self):
        result = True
        financeId = forceRef(self.cmbFinance.value())
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        clientRecord = db.getRecord(tableClient, '*', self.clientId)
        SNILS = forceString(clientRecord.value('SNILS'))
        tableFinance = db.table('rbFinance')
        financeRecord = db.getRecord(tableFinance, '*', financeId)
        finance = forceInt(financeRecord.value('code')) if financeRecord else None
        mkb = forceString(self.cmbMKB.text())
        formularyItemId = forceRef(self.cmbDrug.value())
        dosage = self.edtDosage.text()
        qnt = self.spbQnt.text().toDouble()[0]
        sigma = forceString(self.edtSigna.text())
        duration = forceInt(self.spbDuration.value())
        numPerDay = forceInt(self.spbNumPerDay.value())
        result = result and self.checkClientSocStatus()
        result = result and (financeId or self.checkInputMessage(u'источник финансирования', False, self))
        if finance == 70:
            result = result and (SNILS or self.checkValueMessage(u'Выписка рецепта за счет федерального бюджета пациенту без СНИЛС не допускается! Измените источник финансирования в рецепте или заполните СНИЛС в регистрационной карте пациента', False, self))
        result = result and (checkDiagnosis(mkb, self.edtDate.date()) or self.checkValueMessage(u'Введенный код МКБ не соответствует справочнику', False, self.cmbMKB))
        result = result and (formularyItemId or self.checkInputMessage(u'препарат', False, self))
        result = result and (sigma or self.checkInputMessage(u'порядок приёма', True, self))
        result = result and ((qnt > 0.0001) or self.checkInputMessage(u'количество единиц', False, self))
        result = result and (dosage or self.checkInputMessage(u'дозировку', False, self))
        result = result and (duration > 0 or self.checkInputMessage(u'длительность приёма', False, self))
        result = result and (numPerDay > 0 or self.checkInputMessage(u'количество приёмов в день', False, self))
        return result

    @QtCore.pyqtSlot(int)
    def drugSelected(self, index):
        def isDosageZero(dosage):
            val = unicode(dosage).split(u' ')[0]
            if forceInt(val) == 0:
                return True
            return False

        def extractDosageFromName(name):
            vals = unicode(name).split(u', ')
            if len(vals) >= 4:
                val = vals[3].strip(u' ')
                vals = val.split(u' ')
                if len(vals) == 2:
                    dosage = vals[0]
                elif len(vals) == 3:
                    dosage = vals[1]
                else:
                    dosage = ''
                return dosage
            return u''

        #TODO: mdldml: переписать этот ужас
        drugId = forceInt(self.cmbDrug.value())
        db = QtGui.qApp.db
        stmt = '''SELECT item.name, CONCAT_WS(' ', CAST(item.dosageQnt AS CHAR), dosage.name) AS dosage, item.qnt AS qnt
                  FROM DloDrugFormulary_Item AS item
                  LEFT JOIN dlo_rbDosage AS dosage ON dosage.id = item.dosage_id
                  WHERE item.id = %d AND dosage.name IS NOT NULL AND item.isSprPC = 1
        ''' % drugId
        query = db.query(stmt)
        if query.next():
            dosage = forceString(query.record().value('dosage'))
            if isDosageZero(dosage):
               dosage = extractDosageFromName(forceString(query.record().value('name')))
            qnt = forceInt(query.record().value('qnt'))
            self.edtDosage.setText(dosage)
            self.spbQnt.setValue(qnt)

        context = CInfoContext()
        formularyItem = context.getInstance(CDloDrugFormularyItemInfo, drugId)
        noMnn = formularyItem.mnn.code == u'1'
        if noMnn:
            self.rbtnPrintMNN.setChecked(not noMnn)
            self.rbtnPrintTradeName.setChecked(noMnn)
        self.rbtnPrintMNN.setEnabled(not noMnn)

    @QtCore.pyqtSlot()
    def updateSigna(self):
        dosage = forceString(self.edtDosage.text())
        qnt = forceInt(self.spbQnt.value())
        numPerDay = forceInt(self.spbNumPerDay.value())
        duration = forceInt(self.spbDuration.value())

        if len(dosage) > 0 and qnt > 0 and numPerDay > 0 and duration > 0:
            self.edtSigna.setText(u'по ' + dosage + u' %d раза в день, %d дней' % (numPerDay, duration))

    @QtCore.pyqtSlot(bool)
    def on_rbtnVkYes_toggled(self, checked):
        self.disconnect(self.cmbDrug, QtCore.SIGNAL('currentIndexChanged(int)'), self.drugSelected)
        currentDrug = self.cmbDrug.value()
        formularyFilter = 'master_id = %d' % forceInt(self.drugMasterId)
        if not checked:
            formularyFilter += ' AND federalCode IS NOT NULL AND isSprPC = 1'
        self.cmbDrug.setFilter(formularyFilter, order='`name` ASC')
        self.cmbDrug.setValue(currentDrug)
        self.connect(self.cmbDrug, QtCore.SIGNAL('currentIndexChanged(int)'), self.drugSelected)

    def checkClientSocStatus(self):
        db = QtGui.qApp.db
        socCode = forceString(self.cmbSocCodes.itemData(self.cmbSocCodes.currentIndex()))
        stmt = u'''
        SELECT
            ClientDocument.id,
            ClientSocStatus.begDate,
            ClientDocument.number
        FROM
            ClientSocStatus
            INNER JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
            INNER JOIN ClientDocument ON ClientSocStatus.document_id = ClientDocument.id
            INNER JOIN rbDocumentType ON ClientDocument.documentType_id = rbDocumentType.id
        WHERE
            %s
        '''
        cond = [
            db.table('rbSocStatusType')['code'].eq(socCode),
            db.table('ClientSocStatus')['client_id'].eq(self.clientId),
            db.table('ClientSocStatus')['deleted'].eq(0)
        ]
        query = db.query(stmt % db.joinAnd(cond))
        result = True
        result = result and (query.first()
                             or self.checkValueMessage(u'У указанной льготы нет подтверждающего документа!', False, self))
        record = query.record()
        check = ((forceString(record.value('number')) != '') and (forceString(record.value('begDate')) != ''))
        result = result and (((forceString(record.value('number')) != '') and (forceString(record.value('begDate')) != ''))
                             or self.checkValueMessage(u'Не заполнены реквизиты документа о праве на льготу (наименование, номер или дата)', False, self))
        result = result and ((forceDate(record.value('begDate')).year() > 0)
                             or self.checkValueMessage(u'Не указана дата начала действия для льготы ' + socCode, False, self))
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbSocCodes_currentIndexChanged(self, index):
        self.checkClientSocStatus()

    def saveData(self):
        return self.checkDataEntered()
