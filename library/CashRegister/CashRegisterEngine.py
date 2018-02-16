# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

import re
from PyQt4 import QtGui, QtCore

from CheckItemModel import CCheckItemModel
from Events.Utils import CPayStatus
from library.CashRegister.CashRegisterDriverInfo import CCashRegisterDriverInfo
from library.CashRegister.CashRegisterOperationInfo import CCashRegisterOperationInfo
from library.CashRegister.ECRLogger import CECRLogger
from library.PrintInfo import CInfoProxy, CInfoContext
from library.Utils import forceInt, forceString, forceBool, forceDecimal, forceDouble, log

'''
Created on 19.08.2013

@author: atronah

This module is designed to work with ATOL DTO driver v8.x (www.atol.ru).
'''


class CCashRegister(QtCore.QObject):
    # Сигнал о необходимости вывести сообщение для пользователя (сообщение, выделить_красным)
    showedMessage = QtCore.pyqtSignal(QtCore.QString, bool)
    # Сигнал перехода нв следующий шаг операции (Название шага)
    nextProgressStep = QtCore.pyqtSignal(QtCore.QString)
    # Согнал об отмене формирования чека в результате ошибки
    canceledCheck = QtCore.pyqtSignal()

    errCommunicationTemplate = u'Проблема взаимодействия с драйвером ККМ (%s)'
    errDriverNotInit = u'Драйвер устройства не инициализирован'
    errUndefined = u'<Не определено>'

    exportFileEncodingList = [u'utf8', u'cp1251', u'cp866']
    exportFormatList = [u'txt']
    supportedCheckType = [
        CCashRegisterDriverInfo.CheckType.sale,
        CCashRegisterDriverInfo.CheckType.annulateSale,
        CCashRegisterDriverInfo.CheckType.returnSale
    ]
    floatTemplate = '%0.3f'

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self._lastMessage = u''
        self._isCanceled = False
        self._isComplete = False
        self._testMode = False
        self._isCorrect = True
        self._model = CCheckItemModel(self)
        self._ecrDriver = None
        self.updateDeviceStatus()

        self.lastCheckInfo = {}
        self._operationInfoList = []
        self._operationInfoLogger = None

        self.__initDriver()

    def __del__(self):
        self.close()
        log(logDir=QtGui.qApp.logDir,
            title=u'CCashRegister.__del__',
            message=u'Объект уничтожен.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        log(logDir=QtGui.qApp.logDir,
            title=u'CCashRegister.__exit__',
            message=u'\n'.join([unicode(item) for item in (exc_type, exc_val, exc_tb)]))

    def __initDriver(self):
        self.open()

    def open(self):
        # TODO: atronah: возможно стоит производить проверку на уже инициализированную кассу и удалять ее перед новой инициализацией
        try:
            from win32com.client import Dispatch

            self.showMessage(u'Подключение к драйверу ККМ')
            self._ecrDriver = Dispatch(CCashRegisterDriverInfo.progID)
            self.loadLogicalDeviceInfo()
        except Exception, e:
            self._ecrDriver = None
            self.onError(u'Не удалось подключиться к драйверу устройства (ProgID = "%s", %s)' % (
                CCashRegisterDriverInfo.progID, unicode(e)))

    def close(self):
        if self._ecrDriver:
            self._ecrDriver.Quit()

    def loadLogicalDeviceInfo(self):
        if not self._ecrDriver:
            return

        deviceSettings = self._ecrDriver.DevicesSettings
        deviceSettingsInfo = dict(re.findall(ur'(?P<name>[\w0-9]+)=(?P<value>[\w0-9]+)', deviceSettings))

        countDevices = forceInt(deviceSettingsInfo.get('Count', 0))
        currentDeviceNumber = forceInt(deviceSettingsInfo.get('CurrentDeviceNumber', -1))
        if currentDeviceNumber not in xrange(countDevices):
            return

        for deviceIndex in xrange(countDevices):
            if forceInt(deviceSettingsInfo.get('DeviceNumber%d' % deviceIndex, -1)) != currentDeviceNumber:
                continue
            self._ecrDriver.CurrentDeviceIndex = deviceIndex
            self._ecrDriver.CurrentDeviceNumber = currentDeviceNumber
            if deviceSettingsInfo.has_key('MachineNumber%d' % deviceIndex):
                self._ecrDriver.MachineName = forceString(deviceSettingsInfo['MachineNumber%d' % deviceIndex])
            if deviceSettingsInfo.has_key('PortNumber%d' % deviceIndex):
                self._ecrDriver.PortNumber = forceInt(deviceSettingsInfo['PortNumber%d' % deviceIndex])
            if deviceSettingsInfo.has_key('BaudRate%d' % deviceIndex):
                self._ecrDriver.BaudRate = forceInt(deviceSettingsInfo['BaudRate%d' % deviceIndex])
            if deviceSettingsInfo.has_key('Model%d' % deviceIndex):
                self._ecrDriver.Model = forceString(deviceSettingsInfo['Model%d' % deviceIndex])
            if deviceSettingsInfo.has_key('AccessPassword%d' % deviceIndex):
                self._ecrDriver.AccessPassword = forceString(deviceSettingsInfo['AccessPassword%d' % deviceIndex])
            if deviceSettingsInfo.has_key('UseAccessPassword%d' % deviceIndex):
                self._ecrDriver.UseAccessPassword = forceBool(deviceSettingsInfo['UseAccessPassword%d' % deviceIndex])
            if deviceSettingsInfo.has_key('WriteLogFile%d' % deviceIndex):
                self._ecrDriver.WriteLogFile = forceInt(deviceSettingsInfo['WriteLogFile%d' % deviceIndex])

    def showMessage(self, message, isRed=False):
        self.serviceLog(title=u'SHOW MESSAGE', msg=message)
        self._lastMessage = message
        self.showedMessage.emit(message, isRed)

    def model(self):
        return self._model

    def setOperationInfoLogger(self, logger):
        self._operationInfoLogger = logger if isinstance(logger, CECRLogger) else None

    def operationInfoLogger(self):
        return self._operationInfoLogger

    def clearOperationInfoList(self):
        self._operationInfoList = []

    def updateOperationInfo(self, operationInfo, checkType, checkNumber, checkSumm, closeType, closeDatetime,
                            isExpense):
        if not operationInfo:
            operationInfo = CCashRegisterOperationInfo()

        if checkType in CCashRegisterDriverInfo.CheckType.titles.keys():
            description = CCashRegisterDriverInfo.CheckType.title(checkType)
        else:
            description = u''

        operationInfo.setCheckInfo(
            checkType, checkNumber, checkSumm, closeType, closeDatetime, self._ecrInfo['Operator']
        )
        operationInfo.setDescription(description)
        operationInfo.setDeviceLogicalNumber(self._ecrInfo['LogicalNumber'])
        operationInfo.setDeviceSerialNumber(self._ecrInfo['SerialNumber'])
        operationInfo.setDeviceFiscal(self._ecrInfo['Fiscal'])
        operationInfo.setSession(self._ecrInfo['Session'])
        operationInfo.setExpense(isExpense)
        return operationInfo

    def addOperationInfo(self, operationInfo, itemList=None):
        if not itemList:
            itemList = []
        self._operationInfoList.append((operationInfo, itemList))

    def logOperationInfo(self, operationInfo, itemList):
        if self._operationInfoLogger:
            self.showMessage(u'Запись информации об операции в базу данных')
            self._operationInfoLogger.saveOperationInfo(operationInfo, itemList)

    def operationInfoList(self):
        return list(self._operationInfoList)

    def checkErrorFlags(self):
        u"""Проверка флагов ошибок ККМ"""
        if not self._ecrDriver:
            self.onError(self.errDriverNotInit)
            return

        errCode = self._ecrDriver.ResultCode
        errDescription = self._ecrDriver.ResultDescription
        paramErrCode = self._ecrDriver.BadParam
        paramErrDescription = self._ecrDriver.BadParamDescription

        if errCode != 0:
            paramErrorText = u'(%s: %s)' % (paramErrCode, paramErrDescription) if paramErrCode else ''
            self.onError(u'Ошибка ККМ с кодом %s: %s %s' % (errCode, errDescription, paramErrorText))

    def isCorrect(self, forceCheck=False):
        if forceCheck:
            self.updateDeviceStatus()
        return self._isCorrect

    def onException(self, e):
        message = self.errCommunicationTemplate % unicode(e)
        if hasattr(QtGui.qApp, 'logCurrentException') and callable(QtGui.qApp.logCurrentException):
            QtGui.qApp.logCurrentException()
        self.onError(message)

    def onError(self, message, setIncorrect=True):
        if setIncorrect:
            self._isCorrect = False
        self.showMessage(message, True)

    def setEnabled(self, enabled, isMessageShow=True):
        if not self._ecrDriver:
            self.onError(self.errDriverNotInit)
            return

        if enabled == self.isEnabled():
            return

        try:
            if isMessageShow:
                self.showMessage(u'%s ККМ' % (u'Включение' if enabled else u'Выключение'))

            self._ecrDriver.DeviceEnabled = enabled
            self.checkErrorFlags()
        except Exception, e:
            self.onException(e)

    def isEnabled(self):
        if self._ecrDriver:
            return self._ecrDriver.DeviceEnabled
        return False

    def setWinId(self, winId):
        if not self.isCorrect():
            return
        self._ecrDriver.ApplicationHandle = int(winId)
        self.checkErrorFlags()

    def modeName(self):
        if not self._ecrDriver:
            return u'<Не определено>'
        mode = self._ecrDriver.Mode
        self.checkErrorFlags()
        if not self._isCorrect:
            return u'<Не определено>'
        return CCashRegisterDriverInfo.Mode.title(mode)

    def setMode(self, modeNumber, password):
        if not self.isCorrect():
            return False
        self.showMessage(
            u'Смена режима с "%s" на "%s"' % (self.modeName(), CCashRegisterDriverInfo.Mode.title(modeNumber)))
        self._ecrDriver.Password = password
        self._ecrDriver.Mode = modeNumber
        self._ecrDriver.SetMode()
        self.checkErrorFlags()
        return self.isCorrect()

    def resetMode(self):
        self.showMessage(u'Сброс текущего режима')
        self._ecrDriver.ResetMode()

    def updateDeviceStatus(self):
        self._isCorrect = True
        if self._ecrDriver:
            self.showMessage(u'Запрос информации о ККМ')
            self._ecrDriver.getStatus()
            self.checkErrorFlags()
            CCashRegister.floatTemplate = u'%%0.%df' % self._ecrDriver.PointPosition if self._isCorrect else 3

            if self.isCorrect():
                if not self._ecrDriver.CheckPaperPresent:
                    self.onError(u'Отсутствует бумага в принтере чеков')
                elif not self._ecrDriver.ControlPaperPresent:
                    self.showMessage(u'Отсутствует бумага в принтере контрольной ленты')
                elif self._ecrDriver.CoverOpened:
                    self.onError(u'Открыта крышка ККМ')
                elif self._ecrDriver.ECRError != 0:
                    self.onError(
                        u'Ошибка ККМ с кодом %s: %s' % (self._ecrDriver.ECRError, self._ecrDriver.ECRErrorDescription))
                elif self._ecrDriver.BatteryLow:
                    self.onError(u'Батарея ККМ разряжена')
                # Повторное использование на случай ошибки обращения к свойствам драйвера
                self.checkErrorFlags()

        else:
            self._isCorrect = False

        # TODO: atronah: убедить, что после выключения ККМ это свойство (Model) не обновляются
        modelNo = self._ecrDriver.Model if self._isCorrect else None
        modelName = '%s | %s' % (modelNo, CCashRegisterDriverInfo.Model.title(modelNo)) if self._isCorrect else None

        self._ecrInfo = {u'DeviceNumber': self._ecrDriver.CurrentDeviceNumber if self._isCorrect else None,
                         u'LogicalNumber': self._ecrDriver.LogicalNumber if self._isCorrect else None,
                         u'SerialNumber': self._ecrDriver.SerialNumber if self._isCorrect else None,
                         u'Model': modelName,
                         u'Operator': self._ecrDriver.Operator if self._isCorrect else None,
                         u'Fiscal': bool(self._ecrDriver.Fiscal) if self._isCorrect else None,
                         u'Date': '%s.%s.%s' % (self._ecrDriver.Day,
                                                self._ecrDriver.Month,
                                                self._ecrDriver.Year) if self._isCorrect else self.errUndefined,
                         u'DriverName': (self._ecrDriver.Version, self._ecrDriver.DeviceDescription) if self._isCorrect else (None, None),
                         u'INN': self._ecrDriver.INN if self._isCorrect else self.errUndefined,
                         u'CurrentCheckNumber': self._ecrDriver.CheckNumber if self._isCorrect else None,
                         u'Session': self._ecrDriver.Session + 1 if self._isCorrect else None,
                         u'SessionOpened': self.isSessionOpened() if self._isCorrect else None
                         }

    # end update device status

    def getDeviceInfo(self, forceUpdate=False):
        if forceUpdate:
            self.updateDeviceStatus()
        return self._ecrInfo

    def getPrintInfo(self):
        context = CInfoContext()
        result = {'deviceInfo': CInfoProxy(context, self.getDeviceInfo(forceUpdate=True)),
                  'checkItems': [CInfoProxy(context, checkItem) for checkItem in self.model().items()],
                  'operations': [{'info': CInfoProxy(context, operationInfo),
                                  'checkItems': [CInfoProxy(context, checkItem) for checkItem in itemList]} for
                                 operationInfo, itemList in self.operationInfoList()]}
        return result

    @QtCore.pyqtSlot()
    def cancelProcessing(self):
        self._isCanceled = True

    def isSessionOpened(self):
        # Проверка на случай ККМ с автооткрытием смены при печате первого чека
        if self._ecrDriver:
            modelNo = self._ecrDriver.Model
            if QtGui.qApp.currentOrgInfis() != u'мсч3':
                if modelNo in CCashRegisterDriverInfo.Model.AutoOpennedSessionModelList:
                    return True

            return self._ecrDriver.SessionOpened
        return False

    def serviceLog(self, title=u'Выполнение processCheck', msg=u''):
        log(logDir=QtGui.qApp.logDir, title=title, message=msg, fileName='KKM.log')

    def processCheck(self, checkType, password, operationInfo=None, enableCheckSum=False, doublePrintCheck=False):
        self.serviceLog(
            msg=u"""
[0] Значение аргументов функции `processCheck`:
 * checkType                       = {checkType}
 * password                        = {password}
 * operationInfo.operationTypeId   = {operationTypeId}
 * enableCheckSum                  = {enableCheckSum}
 * doublePrintCheck                = {doublePrintCheck}
""".format(
                checkType=checkType,
                password=password,
                operationTypeId=operationInfo.operationTypeId if operationInfo else operationInfo,
                enableCheckSum=enableCheckSum,
                doublePrintCheck=doublePrintCheck
            )
        )
        result = False
        if not self.isCorrect(True):
            self.serviceLog(msg=u'[0.1] Выход из функции: Состояние ККМ не корректно')
            return result

        if not self.isSessionOpened():
            self.onError(u'Не открыта смена', False)
            return result

        items = self.model().selectedItems()
        if not items:
            self.onError(u'Не выбрано элементов для внесения в чек', False)
            return result

        log(logDir=QtGui.qApp.logDir,
            title=u'Касса. Пытаемся провести операцию',
            message=u'\n'.join([unicode(item) for item in items]))

        self._isCanceled = False
        isOpenned = False

        totalSumm = forceDecimal(0.0)
        newPayStatusInfoList = []
        try:
            self.serviceLog(msg=u'[1] Вход в блок операций')
            if not self.setMode(1, password):  # 1 - Режим регистрации
                return result

            if self.openCheck(checkType):
                self.serviceLog(msg=u'[1.1] Открываем чек: чек открыт')
                isOpenned = True
            else:
                self.serviceLog(msg=u'[1.2] Открываем чек: чек открыть не удалось')
                return result

            self.serviceLog(msg=u'[2] Вход в цикл обработки позиций в чеке')
            for item in items:
                if self._isCanceled or not self.isCorrect():
                    self.serviceLog(msg=u'[2.1.1] Отмена операции /%s/' % item.name)
                    self.cancelCheck()
                    self.nextProgressStep.emit(u'Отменено')
                    break
                else:
                    self.serviceLog(msg=u'[2.1.2] Регистрация позиции чека /%s/' % item.name)
                    self.nextProgressStep.emit(u'Регистрация')

                # Заполняем так, поскольку мало ли при заполнении `self._ecrDriver` летит exception
                self.serviceLog(msg=u"""
[2.2] Заполнение структуры позиции чека
 * checkType        = {checkType} /* CCashRegisterDriverInfo.CheckType */
 * TestMode         = {testMode}
 * TextWrap         = 1  # 0 - нет переноса, 1 - перенос по словам, 2 - перенос по строке
 * Name             = {itemName}
 * Quantity         = {quantity}
 * Price            = {price}
 * Department       = {department}
 * DiscountType     = {discountType}
 * DiscountValue    = {discountValue}
 * TaxTypeNumber    = {vat}
""".format(
                    checkType=checkType,
                    testMode=self._testMode,
                    itemName=item.name,
                    quantity=forceDouble(item.quantity),
                    price=forceDouble(item.price),
                    department=item.department,
                    discountType=item.discountType,
                    discountValue=forceDouble(item.discountValue) if item.discountValue > item.precision else 0.0,
                    vat=item.vat
                ))
                self._ecrDriver.TestMode = self._testMode
                self._ecrDriver.TextWrap = 1  # 0 - нет переноса, 1 - перенос по словам, 2 - перенос по строке
                self._ecrDriver.Name = item.name
                self._ecrDriver.Quantity = forceDouble(item.quantity)
                self._ecrDriver.Price = forceDouble(item.price)
                self._ecrDriver.Department = item.department
                self._ecrDriver.DiscountType = item.discountType
                self._ecrDriver.DiscountValue = forceDouble(item.discountValue) if item.discountValue > item.precision else 0.0
                self._ecrDriver.TaxTypeNumber = item.vat

                self.serviceLog(msg=u'[2.3] Выбор типа операции')
                if checkType == CCashRegisterDriverInfo.CheckType.returnSale:
                    self.serviceLog(msg=u'[2.3.1] Тип операции: ВОЗВРАТ')
                    self.returnSale(item, enableCheckSum)
                    newPayStatus = CPayStatus.exposed
                elif checkType == CCashRegisterDriverInfo.CheckType.annulateSale:
                    self.serviceLog(msg=u'[2.3.2] Тип операции: АННУЛИРОВАНИЕ')
                    self.annulateSale(item, enableCheckSum)
                    newPayStatus = CPayStatus.exposed
                else:
                    self.serviceLog(msg=u'[2.3.1] Тип операции: ПРОДАЖА (РЕГИСТРАЦИЯ)')
                    self.registration(item)
                    newPayStatus = CPayStatus.payed
                self.serviceLog(msg=u'[2.4] Внесение результатов в ВМ /%s/' % item.name)
                newPayStatusInfoList.append((item, newPayStatus))
                item.isSelected = False
                totalSumm += item.quantity * item.price
                QtGui.qApp.processEvents()
                # end for
        except Exception, e:
            self.onException(e)
            if isOpenned:
                self.cancelCheck()
        finally:
            self.serviceLog(msg=u'[3] Выход из цикла обработки позиций чека. Сбрасываем текущий режим ККМ')
            self.resetMode()
            if isOpenned:
                self.serviceLog(msg=u'[3.1] Фиксируем информацию о последнем чеке')
                closeType = forceInt(QtGui.qApp.db.translate('rbECROperationType', 'id', operationInfo.operationTypeId,'code')) or 0  # 0 - наличными
                checkNumber = self.closeCheck(closeType)
                closeDatetime = QtCore.QDateTime.currentDateTime()
                self.lastCheckInfo = {u'CheckNumber': checkNumber,
                                      u'CloseDatetime': closeDatetime,
                                      u'CloseType': u'наличными' if closeType == 0 else closeType,
                                      u'CheckType': checkType,
                                      u'Summ': totalSumm}
                if self.isCorrect():
                    if doublePrintCheck:
                        self.serviceLog(msg=u'[3.2] Печатаем копию последнего чека')
                        self._ecrDriver.PrintLastCheckCopy()

                    self.serviceLog(msg=u'[3.3] Дублирование self.lastCheckInfo в элементы чека')
                    for item, newPayStatus in newPayStatusInfoList:
                        item.payStatus = newPayStatus
                        # TODO: atronah: поразмышлять, действительно ли надо дублировать self.lastCheckInfo в элементы чека... Не помню, зачем это делалось..
                        # Скорее всего, чтобы отличать те элементы, которые попали в последний чек от тех, кто были пропущены.
                        item.lastCheckInfo = dict(self.lastCheckInfo)

                    isExpense = checkType in [checkType == CCashRegisterDriverInfo.CheckType.returnSale,
                                              CCashRegisterDriverInfo.CheckType.annulateSale]

                    self.serviceLog(msg=u'[3.4] Обновление информации о проведенной операции')
                    operationInfo = self.updateOperationInfo(operationInfo=operationInfo,
                                                             checkType=checkType,
                                                             checkNumber=checkNumber,
                                                             checkSumm=totalSumm,
                                                             closeType=closeType,
                                                             closeDatetime=closeDatetime,
                                                             isExpense=isExpense)
                    self.addOperationInfo(operationInfo, items)
                    self.logOperationInfo(operationInfo, items)

        self.serviceLog(msg=u'[4] Проверка флагов ошибок ККМ')
        self.checkErrorFlags()
        self.serviceLog(msg=u'[5] Завершение processCheck с результатом: %s' % (result and self.isCorrect()))
        return result and self.isCorrect()

    def registration(self, item):
        self.showMessage(u'Регистрация продажи (%s)' % item)
        self._ecrDriver.TestMode = self._testMode
        self._ecrDriver.Registration()
        self.checkErrorFlags()

    def annulateSale(self, item, enableCheckSum=False):
        self.showMessage(u'Аннулирование продажи (%s)' % item)
        self._ecrDriver.TestMode = self._testMode
        self._ecrDriver.EnableCheckSumm = enableCheckSum
        self._ecrDriver.Annulate()
        self.checkErrorFlags()

    def returnSale(self, item, enableCheckSum=False):
        self.showMessage(u'Возврат продажи (%s)' % item)
        self._ecrDriver.TestMode = self._testMode
        self._ecrDriver.EnableCheckSumm = enableCheckSum
        self._ecrDriver.Return()
        self.checkErrorFlags()

    def openCheck(self, checkType):
        checkTypeName = CCashRegisterDriverInfo.CheckType.title(checkType)
        if checkType not in self.supportedCheckType:
            self.onError(u'Ошибка открытия чека с типом "%s": не поддерживается клиентским ПО' % checkTypeName, False)
            return False

        # Если чек открыт (в результате какой-нибудь ошибки), то отменить его.
        if self._ecrDriver.CheckState != 0:
            self.cancelCheck()

        self.showMessage(u'Открытие чека (%s)' % checkTypeName)
        self._ecrDriver.TestMode = self._testMode
        self._ecrDriver.CheckType = checkType
        self._ecrDriver.OpenCheck()
        self.lastCheckInfo = {}
        self.checkErrorFlags()
        return self.isCorrect()

    def cancelCheck(self):
        self._ecrDriver.TestMode = self._testMode
        self.showMessage(u'Отмена (аннулирование) чека')
        self._ecrDriver.CancelCheck()
        self.canceledCheck.emit()
        self.checkErrorFlags()

    def closeCheck(self, closeType):
        self.showMessage(u'Закрытие чека')

        if closeType not in xrange(6):
            self.showMessage(u'Неверный тип закрытия чека (%s) был изменен на тип "наличными"' % closeType, True)
            closeType = 0

        self._ecrDriver.TestMode = self._testMode
        self._ecrDriver.TypeClose = closeType
        checkNumber = self._ecrDriver.CheckNumber
        self._ecrDriver.CloseCheck()
        self.checkErrorFlags()
        return checkNumber

    def cut(self, isFull):
        self.showMessage(u'Обрезка чековой ленты (%s)' % (u'Полная' if isFull else u'Частичная'))
        if self._ecrDriver:
            if isFull:
                self._ecrDriver.FullCut()
            else:
                self._ecrDriver.PartialCut()
            if self.checkErrorFlags():
                return True
        return False

    def printReport(self, mode, reportType, password, operationInfo=None):
        reportTypeTitle = CCashRegisterDriverInfo.ReportType.title(reportType)

        if reportType not in CCashRegisterDriverInfo.ReportType.titles.keys():
            self.onError(
                u'Ошибка формирования отчета: выбран неподдерживаемый тип отчета (%s)' % reportTypeTitle, False
            )
            return
        if mode not in (CCashRegisterDriverInfo.Mode.xReport, CCashRegisterDriverInfo.Mode.zReport):
            self.onError(u'Ошибка формирования отчета: выбран неверный режим ККМ (%s)' % mode, False)
            return

        if not self.isCorrect(True):
            return

        operationDescription = u'Формирование %s-отчета: %s' % (
            u'X' if mode == CCashRegisterDriverInfo.Mode.xReport else u'Z',
            CCashRegisterDriverInfo.ReportType.title(reportType))
        self.showMessage(operationDescription)
        try:
            if not self.setMode(mode, password):  # 2 - Режим X-отчетов, 3 - режим Z-отчетов
                return

            checkNumber = self._ecrDriver.CheckNumber
            self._ecrDriver.TestMode = self._testMode
            self._ecrDriver.ReportType = reportType
            self._ecrDriver.Report()
            self.checkErrorFlags()

            if self.isCorrect():
                closeDatetime = QtCore.QDateTime.currentDateTime()
                operationInfo = self.updateOperationInfo(operationInfo=operationInfo,
                                                         checkType=None,
                                                         checkNumber=checkNumber,
                                                         checkSumm=None,
                                                         closeType=None,
                                                         closeDatetime=closeDatetime,
                                                         isExpense=None)
                operationInfo.setDescription(operationDescription)
                self.addOperationInfo(operationInfo=operationInfo,
                                      itemList=[])
                self.logOperationInfo(operationInfo=operationInfo,
                                      itemList=[])
            self.resetMode()
        except Exception, e:
            self.onException(e)

        self.checkErrorFlags()

    def openCashBox(self):
        if not self.isCorrect(True):
            return

        operationDescription = u'Отпправка команды на открытие денежного ящика'
        self.showMessage(operationDescription)

        try:
            self._ecrDriver.TestMode = self._testMode
            self._ecrDriver.OpenDrawer()
            self.checkErrorFlags()
            self.resetMode()
        except Exception, e:
            self.onException(e)
        self.checkErrorFlags()

    def cashMovement(self, isIncome, summ, password, operationInfo=None):
        if not self.isCorrect(True):
            return

        operationDescription = u'Операция по %s денежных средств' % (
            u'внесению в кассу' if isIncome else u'изъятию из кассы')
        self.showMessage(operationDescription)

        try:
            if not self.setMode(CCashRegisterDriverInfo.Mode.registration, password):
                return

            self._ecrDriver.TestMode = self._testMode
            self._ecrDriver.Summ = summ
            checkNumber = self._ecrDriver.CheckNumber
            if isIncome:
                self._ecrDriver.CashIncome()
            else:
                self._ecrDriver.CashOutcome()
            self.checkErrorFlags()
            if self.isCorrect():
                closeDatetime = QtCore.QDateTime.currentDateTime()
                self.lastCheckInfo = {u'CheckNumber': checkNumber,
                                      u'CloseDatetime': closeDatetime,
                                      u'CloseType': u'наличными',
                                      u'CheckType': None,
                                      u'Summ': summ
                                      }

                operationInfo = self.updateOperationInfo(operationInfo=operationInfo,
                                                         checkType=None,
                                                         checkNumber=checkNumber,
                                                         checkSumm=summ,
                                                         closeType=None,
                                                         closeDatetime=closeDatetime,
                                                         isExpense=not isIncome)

                operationInfo.setDescription(operationDescription)
                self.addOperationInfo(operationInfo=operationInfo,
                                      itemList=[])
                self.logOperationInfo(operationInfo=operationInfo,
                                      itemList=[])
            self.resetMode()
        except Exception, e:
            self.onException(e)

        self.checkErrorFlags()

    def openSession(self, password):
        if not self.isCorrect(True):
            return

        if self.isSessionOpened():
            self.showMessage(u'Смена уже открыта')
            return

        if not self.setMode(CCashRegisterDriverInfo.Mode.registration, password):
            return

        nextSession = self._ecrDriver.Session + 1
        operationDescription = u'Открытие смены №%s' % nextSession

        self.showMessage(operationDescription)
        try:
            checkNumber = self._ecrDriver.CheckNumber
            self._ecrDriver.TestMode = self._testMode
            self._ecrDriver.Caption = 'vistamed'
            self._ecrDriver.OpenSession()
            self.checkErrorFlags()
            if self.isCorrect():
                closeDatetime = QtCore.QDateTime.currentDateTime()
                self.lastCheckInfo = {u'CheckNumber': checkNumber,
                                      u'CloseDatetime': closeDatetime,
                                      u'CloseType': u'наличными',
                                      u'CheckType': None,
                                      u'Summ': None}
                operationInfo = self.updateOperationInfo(operationInfo=None,
                                                         checkType=None,
                                                         checkNumber=checkNumber,
                                                         checkSumm=None,
                                                         closeType=None,
                                                         closeDatetime=closeDatetime,
                                                         isExpense=None)
                operationInfo.setDescription(operationDescription)
                self.addOperationInfo(operationInfo=operationInfo,
                                      itemList=[])
                self.logOperationInfo(operationInfo=operationInfo,
                                      itemList=[])
            self.resetMode()
        except Exception, e:
            self.onException(e)

        self.checkErrorFlags()

    @QtCore.pyqtSlot()
    def showProperties(self):
        if not self._ecrDriver:
            self.onError(self.errDriverNotInit)
            return

        self._ecrDriver.DisableParamWindow = True
        self._ecrDriver.ShowProperties()

        self.checkErrorFlags()
