# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

import os
from PyQt4 import QtGui, QtCore

from CashRegisterEngine import CCashRegister
from Orgs.Utils import getOrganisationShortName
from Ui_CashRegisterWindow import Ui_CashRegisterWindow
from library.CashRegister.CashRegisterDriverInfo import CCashRegisterDriverInfo
from library.CashRegister.CashRegisterOperationInfo import COperationInfoDialog
from library.CashRegister.CheckItemModel import CVATItemDelegate
from library.CashRegister.ECRLogger import CECRLogger
from library.PrintTemplates import customizePrintButton, applyTemplate, getFirstPrintTemplate, compileAndExecTemplate, \
    getTemplate
from library.ProcessingDialog import CProcessingDialog
from library.SendMailDialog import sendMailClient
from library.Utils import forceString, forceBool, forceDate, forceInt, getPref, \
    setPref

'''

Created on 26.09.2013

@author: atronah
'''


def getECashRegister(parentDialog, availableOperations=None):
    """
    Создает и настраивает диалоговое окно работы с кассой.


    :type parentDialog: basestring
    :param parentDialog: родительский объект для создаваемого окна.

    :type availableOperations: int
    :param availableOperations: указывает доступные для пользователя возможности модуля (see also :py:meth:`CCashRegisterWindow.availableOperations`)

    :rtype : CCashRegisterWindow
    :return: экземпляр диалога для работы с ККМ.
    """
    ecrDialog = CCashRegisterWindow(parentDialog, preferences=getPref(QtGui.qApp.preferences.appPrefs, 'ECRSettings', {}))
    ecrDialog.setAvailableOperation(availableOperations)
    ecrDialog.setOperationInfoLogger(CECRLogger(QtGui.qApp.db))
    return ecrDialog


class CCashRegisterWindow(QtGui.QDialog, Ui_CashRegisterWindow):
    # Сигнал на проведение на оплату (аргумент определяет, тестовый или нет режим)
    registered = QtCore.pyqtSignal(int)
    # Сигнал на отмену чека
    canceled = QtCore.pyqtSignal()
    # Сигнал на отрезку чековой ленты (аргумент определяет полную ли делать отрезку или нет)
    cut = QtCore.pyqtSignal(bool)
    # Сигнал отмены формирования чека
    cancelProcessing = QtCore.pyqtSignal()

    cancelText = u'Отменить'
    execText = u'Выполнить'

    # битовые значения опции доступных операций
    CheckOperation = 1
    ClippingOperation = 2
    ReportOperation = 4
    OpenSessionOperation = 8
    CashOperation = 16
    ECRSelectOperation = 32

    # Параметры имени генерируемого файла экспорта для 1C
    fileNameLanguages = {
        'titles': [u'Русском', u'Английском'],
        'codes': [u'ru', u'en']
    }

    def __init__(self, parent=None, preferences=None):
        QtGui.QDialog.__init__(self, parent)

        self.actPrintByTemplate = None

        self.setupUi(self)

        self.edtLogging.clear()

        self.progressBar.setRange(0, 0)

        self.enabledDeviceIcon = QtGui.QPixmap(':/new/prefix1/icons/greenDot.png').scaled(16,
                                                                                          16,
                                                                                          QtCore.Qt.KeepAspectRatio,
                                                                                          QtCore.Qt.SmoothTransformation)
        self.disabledDeviceIcon = QtGui.QPixmap(':/new/prefix1/icons/redDot.png').scaled(16,
                                                                                         16,
                                                                                         QtCore.Qt.KeepAspectRatio,
                                                                                         QtCore.Qt.SmoothTransformation)

        self.eCashRegister = CCashRegister()
        self.eCashRegister.showedMessage.connect(self.showMessage)
        self.eCashRegister.nextProgressStep.connect(self.nextProgressStep)

        self.cancelProcessing.connect(self.eCashRegister.cancelProcessing)

        if preferences:
            self.setPreferences(preferences)

        self.eCashRegister.setWinId(self.winId())

        self.checkTypeButtonGroup = QtGui.QButtonGroup()
        self.checkTypeButtonGroup.addButton(self.rbRegistration, 1)
        self.checkTypeButtonGroup.addButton(self.rbAnnulate, 2)
        self.checkTypeButtonGroup.addButton(self.rbReturn, 3)
        self.changeModelSelectControlMode(1)
        self.connect(self.checkTypeButtonGroup, QtCore.SIGNAL('buttonClicked(int)'), self.changeModelSelectControlMode)

        self.tblItems.setModel(self.eCashRegister.model())
        self.tblItems.setItemDelegateForColumn(5, CVATItemDelegate(self.tblItems))
        self.eCashRegister.model().showedMessage.connect(self.showMessage)
        self.eCashRegister.model().modelReset.connect(self.updateCheckTotalInfo)
        self.eCashRegister.model().dataChanged.connect(self.updateCheckTotalInfo)

        self.setAvailableOperation(None)  # Поддержка всех операций по умолчанию

        self._isProcessing = False
        self._exportInfo = {}

        # Иницициализация списка действий с деньгами
        self.cmbCashMovement.addItems(
            [u'<Выберите действие>', u'Внесение денежных средств', u'Изъятие денежных средств']
        )

        # Иницициализация списка отчетов
        self.cmbReportType.addItems([u'<Выберите отчет>', u'X-отчет без гашения', u'Z-отчет с гашением'])

        customizePrintButton(self.btnPrintByTemplate, 'ecr')
        self.connect(self.btnPrintByTemplate, QtCore.SIGNAL('printByTemplate(int)'), self.applyPrintTemplate)

        self.cmbFileNameLanguage.addItems(self.fileNameLanguages['titles'])

        self.updateECRInfo()

        self.edtExportDir.setText(QtCore.QDir.homePath())

        self.cmbExportFileEncoding.addItems(self.eCashRegister.exportFileEncodingList)
        self.cmbExportFileEncoding.setCurrentIndex(0)

        self.cmbExportFormat.addItems(self.eCashRegister.exportFormatList)
        self.cmbExportFormat.setCurrentIndex(0)

        self._operationInfoLogger = None

        self.edtExportBegDate.setCalendarPopup(True)
        self.edtExportBegDate.setDate(QtCore.QDate.currentDate())
        self.edtExportEndDate.setCalendarPopup(True)
        self.edtExportEndDate.setDate(QtCore.QDate.currentDate())
        self.chkExportDateEnabled.setChecked(False)

        self.chkExportCheckNumberEnabled.setChecked(False)

        self.updateItemInfo()

        self._additionalPrintInfo = {}

    def addInfoForPrint(self, name, info):
        self._additionalPrintInfo[name] = info

    @QtCore.pyqtSlot(int)
    def applyPrintTemplate(self, templateId):
        info = self._additionalPrintInfo
        info.update(self.eCashRegister.getPrintInfo())
        applyTemplate(self, templateId, info)

    def setOperationInfoLogger(self, logger):
        self._operationInfoLogger = logger if isinstance(logger, CECRLogger) else None
        self.eCashRegister.setOperationInfoLogger(logger)

    def operationInfoLogger(self):
        return self._operationInfoLogger

    def setExportInfo(self, infoDict):
        self._exportInfo = infoDict

    def getOperationInfo(self, cashFlowArticle=None):
        operationInfoDialog = COperationInfoDialog(self)
        operationInfoDialog.setPersonName(forceString(self._exportInfo.get('personName', u'')))
        isNaturalPerson = forceBool(self._exportInfo.get('isNaturalPerson', False))
        operationInfoDialog.setPersonNatural(isNaturalPerson)

        operationInfoDialog.setDocumentTypeList(self._exportInfo.get('documentTypeList', [u'паспорт']))
        if isNaturalPerson and self.chkFillPersonDocument.isChecked():
            operationInfoDialog.setDocumentType(forceInt(self._exportInfo.get('documentTypeIndex', -1)))
            operationInfoDialog.setDocumentSerial(forceString(self._exportInfo.get('documentSerial', u'')))
            operationInfoDialog.setDocumentNumber(forceString(self._exportInfo.get('documentNumber', u'')))
            operationInfoDialog.setDocumentIssuedDate(
                forceDate(self._exportInfo.get('documentIssuedDate', QtCore.QDate())))
            operationInfoDialog.setDocumentIssued(forceString(self._exportInfo.get('documentIssued', u'')))

        operationInfoDialog.setPersonINN(forceString(self._exportInfo.get('personINN', u'')))
        operationInfoDialog.setSubstructure(forceString(self._exportInfo.get('substructure', u'')))

        if cashFlowArticle is None:
            cashFlowArticle = forceString(self._exportInfo.get('itemsCashFlowArticle', u''))
        operationInfoDialog.setCashFlowArticle(cashFlowArticle)
        if self._operationInfoLogger:
            operationInfoDialog.setTypesInfo(self._operationInfoLogger.operationTypesInfo())
        operationInfoDialog.setTypeId(None)

        if operationInfoDialog.exec_():
            operationInfo = operationInfoDialog.opearationInfo()
            self._exportInfo['personName'] = operationInfo.personName
            self._exportInfo['personINN'] = operationInfo.personINN
            self._exportInfo['isNaturalPerson'] = operationInfo.isPersonNatural
            self._exportInfo['documentSerial'] = operationInfo.personDocumentSerial
            self._exportInfo['documentNumber'] = operationInfo.personDocumentNumber
            self._exportInfo['documentIssuedDate'] = operationInfo.personDocumentIssuedDate
            self._exportInfo['documentIssued'] = operationInfo.personDocumentIssued
            self._exportInfo['substructure'] = operationInfo.substructure
            self._exportInfo['typeId'] = operationInfo.operationTypeId
            return operationInfo

        # self.showMessage(u'Отменено пользователем в процессе указания параметров операции', True)
        return None

    def setPassword(self, password):
        self.edtPassword.setText(password)
        self.chkRemeberPassword.setChecked(bool(password))

    def password(self):
        return self.edtPassword.text() if self.chkRemeberPassword.isChecked() else QtCore.QString()

    def setExportDir(self, exportDir):
        self.edtExportDir.setText(exportDir)

    def exportDir(self):
        return self.edtExportDir.text()

    def availableOperations(self):
        """
        Возвращает флаги доступа к функциям модуля работы с кассой.
        Возможные значения флагов (можно комбинировать/складывать)
            * CCashRegisterWindow.CheckOperation - операции по формированию чека продажи/возврата/аннулирования.
            * CCashRegisterWindow.ClippingOperation - операции по полной/частичной обрезке чековой ленты.
            * CCashRegisterWindow.ReportOperation - операции по формированию отчетов на ККМ.
            * CCashRegisterWindow.OpenSessionOperation - право открывать смену.
            * CCashRegisterWindow.CashOperation - операции по внесению/изъятию денежных средств
            * CCashRegisterWindow.ECRSelectOperation - доступ к окну выбора ККМ, предостовляемого драйвером ККМ.

        :rtype : int
        :return: доступные для пользователя возможности модуля.
        """
        return self._availableOperations

    # TODO: atronah: доработать с учетом новых возможностей и сделать доступным для использования из интерфейса
    def setAvailableOperation(self, availableOperations):
        u"""
        Включение/выключение компонентов формы в соответствии с битовой маской
        :param availableOperations: битовая маска доступности компонентов формы
        № бита (значение если включено) - описание
            0 (1) - Продажа/Аннулирование/Возврат продажи
            1 (2) - Отрезка чековой ленты
            2 (4) - Отчеты
            3 (8) - Открытие смены
            4 (16) - Операции с деньгами
            5 (32) - Диалог выбора ККМ
        :return:
        """
        if availableOperations is None:
            availableOperations = self.CheckOperation | self.ClippingOperation \
                                  | self.ReportOperation | self.OpenSessionOperation \
                                  | self.CashOperation | self.ECRSelectOperation

        self._availableOperations = availableOperations

        check = bool(availableOperations & self.CheckOperation)
        clipping = bool(availableOperations & self.ClippingOperation)
        reports = bool(availableOperations & self.ReportOperation)
        deviceInfo = self.eCashRegister.getDeviceInfo(False)
        session = bool(availableOperations & self.OpenSessionOperation) and not deviceInfo.get(u'SessionOpened', False)
        cash = bool(availableOperations & self.CashOperation)
        ecrSelect = bool(availableOperations & self.ECRSelectOperation)

        self.tabRegistration.setEnabled(check)
        self.tabOther.setEnabled(cash or clipping or session or reports)
        self.btnOpenSession.setEnabled(session)
        self.gbCashMovement.setEnabled(cash)
        self.gbClipping.setEnabled(clipping)
        self.btnBrowseECR.setEnabled(ecrSelect)
        for tabIndex in xrange(self.tabWidget.count()):
            if self.tabWidget.widget(tabIndex).isEnabled():
                self.tabWidget.setCurrentIndex(tabIndex)
                break

    def setItems(self, items):
        model = self.eCashRegister.model()
        self.eCashRegister.clearOperationInfoList()
        if model:
            model.setItems(items)
            self.tblItems.resizeColumnsToContents()

    def items(self):
        model = self.eCashRegister.model()
        if model:
            return model.items()
        return []

    # TODO: atronah: довести до рабочего состояния
    @QtCore.pyqtSlot()
    def updateItemInfo(self):
        info = forceString(self.tblItems.currentIndex().data(QtCore.Qt.ToolTipRole))
        if info:
            self.lblItemInfo.setText(info)
        else:
            self.lblItemInfo.setText(u'')

    def updateECRInfo(self):
        def getPropertyName(value):
            if value is None:
                return u'<Не определено>'
            return unicode(value)

        # end func
        try:
            self.setECREnabled(True)
            info = self.eCashRegister.getDeviceInfo(True)
        finally:
            self.setECREnabled(False)

        sessionOpened = info.get(u'SessionOpened', False)
        session = info[u'Session'] if sessionOpened else None
        self.lblECRNumber.setText(getPropertyName(info[u'DeviceNumber']))
        self.lblModeName.setText(self.eCashRegister.modeName())
        self.lblOperatorName.setText(getPropertyName(info[u'Operator']))
        self.lblFiscalEnabledState.setText(getPropertyName(info[u'Fiscal']))
        self.lblECRDate.setText(getPropertyName(info[u'Date']))
        self.lblDriverName.setText(getPropertyName(info[u'DriverName'][1]))
        self.lblModel.setText(getPropertyName(info[u'Model']))
        self.lblINN.setText(getPropertyName(info[u'INN']))
        self.lblCurrentCheckNumber.setText(getPropertyName(info[u'CurrentCheckNumber']))
        self.lblCurrentSession.setText(getPropertyName(session))
        self.spbExportSession.setValue(forceInt(info[u'Session']))
        self.spbExportCheckNumber.setValue(forceInt(info[u'CurrentCheckNumber']))

        availableOpenSession = bool(self._availableOperations & self.OpenSessionOperation)

        if QtGui.qApp.currentOrgInfis() == u'мсч3':
            self.btnOpenSession.setEnabled(True)
        else:
            self.btnOpenSession.setEnabled(not sessionOpened and availableOpenSession)

    def setECREnabled(self, enabled):
        self.eCashRegister.setEnabled(enabled, False)
        isEnabled = self.eCashRegister.isEnabled()
        self.lblDeviceStateIcon.setPixmap(self.enabledDeviceIcon if isEnabled else self.disabledDeviceIcon)

    @QtCore.pyqtSlot()
    def updateCheckTotalInfo(self):
        model = self.tblItems.model()
        if model:
            self.lblCheckTotalInfo.setText(u'Элементов чека: %d, Итоговая сумма: %0.3f (С учетом скидок: %0.3f)' % (
                len(model.selectedItems()), model.totalSumm(), model.totalSumm(withDiscount=True)
            ))

    def setInterfaceBlocking(self, isBlocking):
        self.tabOther.setEnabled(not isBlocking)
        self.tabSettings.setEnabled(not isBlocking)
        self.gbCheckType.setEnabled(not isBlocking)
        self.btnStartStop.setText(self.execText if not isBlocking else self.cancelText)
        self.tblItems.setEnabled(not isBlocking)
        self.chkEnableCheckSum.setEnabled(not isBlocking and not self.rbRegistration.isChecked())
        self.btnBrowseECR.setEnabled(not isBlocking and (self._availableOperations & self.ECRSelectOperation))
        if not isBlocking:
            self.updateECRInfo()

    def closeEvent(self, event):
        if self._isProcessing:
            event.ignore()
        else:
            self.setECREnabled(False)
            self.setResult(QtGui.QDialog.Accepted)
            event.accept()

    def setPreferences(self, preferences):
        operatorPassword = forceString(getPref(preferences, 'operatorPassword', u''))
        self.setPassword(operatorPassword)
        self.chkRemeberPassword.setChecked(bool(operatorPassword))

        self.chkAutoExportDuringZReport.setChecked(forceBool(getPref(preferences, 'isAutoExportDuringZReport', True)))
        self.edtExportDir.setText(forceString(getPref(preferences, 'exportDir', QtCore.QDir.homePath())))
        exportEncoding = forceString(getPref(preferences, 'exportEncoding', 'utf8'))
        self.cmbExportFileEncoding.setCurrentIndex(self.cmbExportFileEncoding.findText(exportEncoding,
                                                                                       flags=QtCore.Qt.MatchExactly))
        exportFormat = forceString(getPref(preferences, 'exportFormat', 'txt'))
        self.cmbExportFormat.setCurrentIndex(self.cmbExportFormat.findText(exportFormat,
                                                                           flags=QtCore.Qt.MatchExactly))
        self.chkFillPersonDocument.setChecked(forceBool(getPref(preferences, 'fillPersonDocument', False)))

        fileNameLangCode = forceString(getPref(preferences, 'fileNameLangCode', u'ru'))
        fileNameLangIdx = 0
        if fileNameLangCode in self.fileNameLanguages['codes']:
            fileNameLangIdx = self.fileNameLanguages['codes'].index(fileNameLangCode)
        self.cmbFileNameLanguage.setCurrentIndex(fileNameLangIdx)

        self.chkDoublePrintCheck.setChecked(forceBool(getPref(preferences, 'doublePrintCheck', False)))

    def preferences(self):
        preferences = {}

        setPref(preferences, 'operatorPassword', self.password())
        setPref(preferences, 'isAutoExportDuringZReport', self.chkAutoExportDuringZReport.isChecked())
        setPref(preferences, 'exportDir', self.edtExportDir.text())
        setPref(preferences, 'exportEncoding', self.cmbExportFileEncoding.currentText())
        setPref(preferences, 'exportFormat', self.cmbExportFormat.currentText())
        setPref(preferences, 'fillPersonDocument', self.chkFillPersonDocument.isChecked())
        setPref(preferences, 'doublePrintCheck', self.chkDoublePrintCheck.isChecked())

        return preferences

    @QtCore.pyqtSlot()
    def on_btnStartStop_clicked(self):
        if self._isProcessing:
            self.cancelProcessing.emit()
            self.setInterfaceBlocking(False)
            self._isProcessing = False
            self.eCashRegister.canceledCheck.disconnect(self.on_btnStartStop_clicked)
        else:
            if not self.eCashRegister.model().selectedItems():
                self.showMessage(u'Не выбрано элементов для выставления', True)
                return
            operationInfo = self.getOperationInfo(None)
            if operationInfo is None:
                return
            if self.rbAnnulate.isChecked():
                checkType = CCashRegisterDriverInfo.CheckType.annulateSale
            elif self.rbReturn.isChecked():
                checkType = CCashRegisterDriverInfo.CheckType.returnSale
            else:
                checkType = CCashRegisterDriverInfo.CheckType.sale

            self.eCashRegister.canceledCheck.connect(self.on_btnStartStop_clicked)

            password = unicode(self.edtPassword.text())
            enableCheckSum = self.chkEnableCheckSum.isChecked()

            doublePrintCheck = int(self.chkDoublePrintCheck.isChecked())

            self.progressBar.setRange(0, len(self.eCashRegister.model().items()))
            self.progressBar.setValue(0)

            self._isProcessing = True

            self.setInterfaceBlocking(True)
            try:
                self.setEnabled(False)
                self.setECREnabled(True)

                dialog = CProcessingDialog(
                    self.eCashRegister.processCheck,
                    (checkType, password, operationInfo, enableCheckSum, doublePrintCheck),
                    parent=self,
                    waitTime=20
                )
                dialog.exec_()

                if dialog.isTerminated:
                    self.eCashRegister.onError(u'Не удалось выполнить операцию: кассовый аппарат не отвечает. Повторите операцию.')
                    self.eCashRegister.close()
                    self.eCashRegister.showMessage(u'Перезагрузка драйвера...')
                    self.eCashRegister.open()
                    self.eCashRegister.resetMode()
            finally:
                self.setEnabled(True)
                self.setECREnabled(False)

            self.setInterfaceBlocking(False)
            self._isProcessing = False
            self.progressBar.setRange(0, 0)
            self.progressBar.setValue(0)

    @QtCore.pyqtSlot(QtCore.QString, bool)
    def showMessage(self, message, isRed=False):
        timeStamp = QtCore.QDateTime.currentDateTime().toString('[dd.MM.yy hh:mm:ss]')
        message = timeStamp + ' ' + message
        if isRed:
            message = u'<span style="color:red">%s</span>' % message
        self.edtLogging.appendHtml(message)

    @QtCore.pyqtSlot(QtCore.QString)
    def nextProgressStep(self, message):
        self.progressBar.setValue(self.progressBar.value() + 1)
        self.progressBar.setFormat(message + u' %p%')

    @QtCore.pyqtSlot()
    def on_btnBrowseECR_clicked(self):
        self.eCashRegister.showProperties()
        self.updateECRInfo()

    @QtCore.pyqtSlot()
    def on_btnFullCut_clicked(self):
        self.setInterfaceBlocking(True)
        try:
            self.setECREnabled(True)
            self.eCashRegister.cut(True)
        finally:
            self.setECREnabled(False)
        self.setInterfaceBlocking(False)

    @QtCore.pyqtSlot()
    def on_btnApplyDiscount_clicked(self):
        self.eCashRegister.model().applyDiscount(self.dsbDiscount.value(),
                                                 CCashRegisterDriverInfo.DiscountType.percent)

    def getCheckClient(self):
        items = self.tblItems.model().selectedItems()
        clientIds = [item._clientId for item in items if item._clientId is not None]
        return clientIds[0] if clientIds else None

    def formatCheck(self):
        data = {
            'items': self.tblItems.model().selectedItems()
        }
        printTemplate = getFirstPrintTemplate('check')
        if printTemplate is not None:
            template = getTemplate(printTemplate[1])

            content, _ = compileAndExecTemplate(template[1], data)
            return content
        return u''

    @QtCore.pyqtSlot()
    def on_btnSendMail_clicked(self):
        selectedItems = self.tblItems.model().selectedItems()
        if selectedItems:
            clientId = self.getCheckClient()
            subject = getOrganisationShortName(QtGui.qApp.currentOrgId())
            sendMailClient(self, clientId, subject, self.formatCheck())
        else:
            QtGui.QMessageBox.information(self,
                                          u'Внимание',
                                          u'Не выбраны позиции для отправки',
                                          QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_btnPartialCut_clicked(self):
        self.setInterfaceBlocking(True)
        try:
            self.setECREnabled(True)
            self.eCashRegister.cut(False)
        finally:
            self.setECREnabled(False)
        self.setInterfaceBlocking(False)

    @QtCore.pyqtSlot()
    def on_btnPrintReport_clicked(self):
        if self.cmbReportType.currentIndex() == 1:  # X-отчет без гашения
            reportMode = 2  # X-Отчеты (без гашения)
            reportType = 2  # Суточный отчет без гашения
        elif self.cmbReportType.currentIndex() == 2:  # Z-отчет с гашением
            userChoise = QtGui.QMessageBox.question(self,
                                                    u'Подтвердите операцию',
                                                    u'Вы собираетесь сформировать Z-отчет с гашением\n'
                                                    u'Это приведет к закрытию смены.\n'
                                                    u'Продолжить',
                                                    buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel,
                                                    defaultButton=QtGui.QMessageBox.Cancel)
            if userChoise != QtGui.QMessageBox.Yes:
                self.showMessage(u'Печать отчета отменена пользователем')
                return
            reportMode = 3  # Z-Отчеты (с гашением)
            reportType = 1  # Суточный отчет с гашением

            if self._operationInfoLogger and self.chkAutoExportDuringZReport.isChecked():
                info = self.eCashRegister.getDeviceInfo(True)
                session = forceInt(info.get('Session', -1))
                exportFormat = forceString(self.cmbExportFormat.currentText()) or 'txt'
                exportEncoding = forceString(self.cmbExportFileEncoding.currentText()) or 'utf8'
                self._operationInfoLogger.export({'session': session,
                                                  'encoding': exportEncoding,
                                                  'format': exportFormat
                                                  })
        else:
            self.showMessage(u'Не выбран тип отчета', True)
            return

        self.setInterfaceBlocking(True)
        try:
            self.setECREnabled(True)
            self.eCashRegister.printReport(reportMode, reportType, unicode(self.edtPassword.text()))
        finally:
            self.setECREnabled(False)
        self.setInterfaceBlocking(False)

    @QtCore.pyqtSlot()
    def on_btnOpenCashBox_clicked(self):
        try:
            self.setECREnabled(True)
            self.eCashRegister.openCashBox()
        finally:
            self.setECREnabled(False)

    @QtCore.pyqtSlot()
    def on_btnCashMovementExecute_clicked(self):
        if self.cmbCashMovement.currentIndex() not in (1, 2):
            self.showMessage(u'Не выбран тип денежной операции', True)
            return

        isIncome = self.cmbCashMovement.currentIndex() == 1  # Внесение

        cashFlowArticle = u'%s денежных средств' % (u'Внесение в кассу' if isIncome else u'Изъятие из кассы')
        operationInfo = self.getOperationInfo(cashFlowArticle)
        if operationInfo is None:
            return

        self.setInterfaceBlocking(True)
        try:
            self.setECREnabled(True)
            self.eCashRegister.cashMovement(isIncome,
                                            self.spbCashMovementAmount.value(),
                                            unicode(self.edtPassword.text()),
                                            operationInfo=operationInfo)
        finally:
            self.setECREnabled(False)
        self.setInterfaceBlocking(False)

    @QtCore.pyqtSlot()
    def on_btnOpenSession_clicked(self):
        self.setInterfaceBlocking(True)
        try:
            self.setECREnabled(True)
            self.eCashRegister.openSession(forceString(self.edtPassword.text()))
        finally:
            self.setECREnabled(False)
        self.setInterfaceBlocking(False)

    @QtCore.pyqtSlot(int)
    def changeModelSelectControlMode(self, buttonId):
        if buttonId == 2:
            checkType = CCashRegisterDriverInfo.CheckType.annulateSale
        elif buttonId == 3:
            checkType = CCashRegisterDriverInfo.CheckType.returnSale
        else:
            checkType = CCashRegisterDriverInfo.CheckType.sale
        # Смена режима контроля выбора элементов в модели в зависимости от типа чека
        self.eCashRegister.model().setCurrentCheckType(checkType)

    @QtCore.pyqtSlot()
    def on_btnExportDirBrowse_clicked(self):
        currentOutDir = self.edtExportDir.text()
        exportOutDurectory = forceString(QtGui.QFileDialog.getExistingDirectory(self,
                                                                                u'Выберите директорию для файлов экспорта в 1С',
                                                                                currentOutDir if os.path.isdir(
                                                                                    currentOutDir) else QtCore.QDir.homePath(),
                                                                                ))
        self.edtExportDir.setText(exportOutDurectory if os.path.isdir(exportOutDurectory) else QtCore.QDir.homePath())

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        if not self._operationInfoLogger:
            self.showMessage(u'Отсуствует модуль экспорта, обратитесь в тех.поддержку', True)
            return
        exportOutDir = forceString(self.edtExportDir.text())
        exportFormat = forceString(self.cmbExportFormat.currentText()) or 'txt'
        exportEncoding = forceString(self.cmbExportFileEncoding.currentText()) or 'utf8'
        exportSession = forceInt(self.spbExportSession.value()) if self.chkExportSessionEnabled.isChecked() else None
        exportBegDate = forceDate(self.edtExportBegDate.date()) if self.chkExportDateEnabled.isChecked() else None
        exportEndDate = forceDate(self.edtExportEndDate.date()) if self.chkExportDateEnabled.isChecked() else None
        exportCheckNumber = forceInt(
            self.spbExportCheckNumber.value()) if self.chkExportCheckNumberEnabled.isChecked() else None
        fileNameLangCode = self.fileNameLanguages['codes'][self.cmbFileNameLanguage.currentIndex()]
        exportParams = {'encoding': exportEncoding,
                        'format': exportFormat,
                        'session': exportSession,
                        'begDate': exportBegDate,
                        'endDate': exportEndDate,
                        'checkNumber': exportCheckNumber,
                        'langCode': fileNameLangCode,
                        'outDir': exportOutDir
                        }
        self.showMessage(u'Начат экспорт данных в файл')
        fileName, operationsCount, errorMessage = self._operationInfoLogger.export(exportParams)
        if fileName:
            self.showMessage(u'Экспорт %s операций успешно завершен (файл экспорта: "%s"' % (operationsCount,
                                                                                             fileName))
        else:
            self.showMessage(u'Ошибка экспорта (%s)' % errorMessage, True)


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pacs',
        'port': 3306,
        'database': 's11vm',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CCashRegisterWindow(None)
    w.exec_()


if __name__ == '__main__':
    main()
