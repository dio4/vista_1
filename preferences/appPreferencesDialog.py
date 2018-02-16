# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# редактор разных умолчаний
import os
import re
from PyQt4 import QtCore, QtGui

from Exchange.R23.attach.Service import CR23LoginAccessService
from Exchange.R78.FssLn.LnService import LnService
from Exchange.R90.IINService.IINService import CR90IINService
from Exchange.TF23Ident.Service import CTF23IdentService
from Exchange.TF78Ident.Service import CTF78IdentService
from KLADR.Utils import getProvinceKLADRCode
from Orgs.Orgs import selectOrganisation
from ScardsModule.scard import Scard
from Ui_appPreferencesDialog import Ui_appPreferencesDialog
from Users.DirtyCrypt import decryptPassword, encryptPassword
from Users.Rights import urAccessRefPersonPersonal, urAdmin
from library import database
from library.ElectronicQueue.EQPanel import SerialScan
from library.Preferences import isPython27
from library.TableModel import CTableModel, CTextCol
from library.Utils import forceBool, forceInt, forceRef, forceString, forceStringEx, toVariant

if isPython27():
    from Exchange.MIP.MIPWinSrv import CMIPWinSrv
    from Exchange.MIP.WSMCC import CWSMCC

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

DefaultSMTPPort = 25
DefaultAverageDuration = 28


class CAppPreferencesDialog(QtGui.QDialog, Ui_appPreferencesDialog):
    noneText = u'Не задано'

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        if not QtGui.qApp.region() == '23':
            self.grpAttach.setVisible(False)
        if not QtGui.qApp.region() == '90':
            self.grpKzCheckIIN.setVisible(False)
        else:
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTerFund),
                                      _translate("appPreferencesDialog", "РПН", None))

        # i3213 Вкладки для КК
        if not ((QtGui.qApp.userHasRight(urAccessRefPersonPersonal) or QtGui.qApp.userHasRight(urAdmin))
                and QtGui.qApp.region().startswith('23')):
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabPersonSync))
        if not QtGui.qApp.region().startswith('23'):
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabRecipes))

        # i3213 Вкладки для СПб
        if not QtGui.qApp.region().startswith('78'):
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabEIS))
            self.chkLoadAttach.setVisible(False)

        # i3213 Скрываем "Регистр диабета" ибо не нужен
        self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabDiabetRegistry))

        self.cmbProvince.setAreaSelectable(True)
        self.portValidator = QtGui.QIntValidator(1, 99999, self)
        self.edtSMTPPort.setValidator(self.portValidator)
        self.cmbTempInvalidDoctype.setTable('rbTempInvalidDocument', True, 'type=0')
        self.cmbTempInvalidReason.setTable('rbTempInvalidReason', True, 'type=0')
        self.cmbHospitalizationDefaultEventType.setTable('EventType')
        if 'QPrinterInfo' in QtGui.__dict__:  # work-around for current version of pyqt in ubuntu 8.04
            printerNames = [unicode(pi.printerName()) for pi in QtGui.QPrinterInfo.availablePrinters()]
        else:
            printerNames = []
        printerNames.insert(0, '')
        self.cmbLabelPrinter.addItems(printerNames)

        self.modelGlobalPreferences = CGlobalPreferencesModel(self)
        self.selectionModelGlobalPreferences = QtGui.QItemSelectionModel(self.modelGlobalPreferences, self)
        self.tblGlobal.setModel(self.modelGlobalPreferences)
        self.tblGlobal.setSelectionModel(self.selectionModelGlobalPreferences)

        comPortsList = SerialScan()
        for comPort in comPortsList:
            self.cmbBarCodeReader.addItem(comPort)

        if not forceRef(QtGui.qApp.db.translate('rbCounter', 'code', 'contract', 'id')):
            self.chkUseCounterInContracts.setEnabled(False)
            self.chkUseCounterInAccounts.setEnabled(False)
            hint = u'''
Для возможности использования счетчика в договорах и/или счетах необходимо создать тип счетчика с кодом 'contract'.
Сделать это можно через пункт меню "Настройки->Счетчики".
'''
            self.chkUseCounterInContracts.setToolTip(hint)
            self.chkUseCounterInAccounts.setToolTip(hint)

        # i3805
        if QtGui.qApp.region() == '78':
            self.lblAverageDuration.setVisible(False)
            self.edtAverageDuration.setVisible(False)

        self.chkAutoPrimacy.clicked.connect(self.f025PrimacySync)
        # ЭПОМС
        # i2340
        try:
            for x in Scard().getCardReaderList():
                self.cmbScardName.addItem(x)
        except Exception as e:
            print '[getCardReaderList] %s' % e.msg if hasattr(e, 'msg') else e.message

        if u'онко' not in QtGui.qApp.currentOrgInfis():
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabAlfalab))
        # self.chkPrintPreview.setVisible(False)

    def f025PrimacySync(self):
        self.cmbF025DefaultPrimacy.setEnabled(not self.chkAutoPrimacy.isChecked())
        self.lblF025DefaultPrimacy.setEnabled(not self.chkAutoPrimacy.isChecked())

    def setTabGlobalEnabled(self, value):
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tabGlobal), value)
        if value:
            self.refreshGlobalPreferences()

    def refreshGlobalPreferences(self):
        self.modelGlobalPreferences.setIdList(QtGui.qApp.db.getIdList('GlobalPreferences'))

    def setProps(self, props):
        global DefaultSMTPPort

        self.cmbOrganisation.setValue(forceRef(props.get('orgId', QtCore.QVariant())))
        self.cmbOrgStructure.setValue(forceRef(props.get('orgStructureId', QtCore.QVariant())))
        self.chkFilterPaymentByOrgStructure.setChecked(
            forceBool(props.get('filterPaymentByOrgStructure', QtCore.QVariant())))
        self.chkOrgStructurePriorityForAddActions.setChecked(
            forceBool(props.get('orgStructurePriorityForAddActions', QtCore.QVariant())))
        kladrCode = forceString(props.get('defaultKLADR', '7800000000000'))
        self.cmbDefaultCity.setCode(kladrCode)
        provinceKLADR = forceString(props.get('provinceKLADR', ''))
        self.cmbProvince.setCode(provinceKLADR or getProvinceKLADRCode(kladrCode))
        self.edtSMTPServer.setText(forceString(props.get('SMTPServer', QtCore.QVariant())))
        port = forceInt(props.get('SMTPPort', QtCore.QVariant()))
        self.edtSMTPPort.setText(str(port if port > 0 else DefaultSMTPPort))
        self.edtMailAddress.setText(forceString(props.get('mailAddress', QtCore.QVariant())))
        self.chkSMTPAuthentification.setChecked(forceBool(props.get('SMTPAuthentification', QtCore.QVariant())))
        self.edtSMTPLogin.setText(forceString(props.get('SMTPLogin', QtCore.QVariant())))
        self.edtSMTPPassword.setText(forceString(props.get('SMTPPassword', QtCore.QVariant())))
        self.edtSMTPLogin.setEnabled(self.chkSMTPAuthentification.isChecked())
        self.edtSMTPPassword.setEnabled(self.chkSMTPAuthentification.isChecked())

        self.cmbDriverName.setEditText(forceString(props.get('EIS_driverName', QtCore.QVariant())))
        self.edtServerName.setText(forceString(props.get('EIS_serverName', QtCore.QVariant())))
        self.edtServerPort.setValue(forceInt(props.get('EIS_serverPort', QtCore.QVariant())))
        self.edtDatabaseName.setText(forceString(props.get('EIS_databaseName', QtCore.QVariant())))
        self.edtUserName.setText(forceString(props.get('EIS_userName', QtCore.QVariant())))
        self.edtPassword.setText(forceString(props.get('EIS_password', QtCore.QVariant())))
        self.edtCodepage.setText(forceString(props.get('EIS_codepage', QtCore.QVariant())))

        socCardSupport = forceBool(props.get('SocCard_SupportEnabled', False))
        self.chkEnableSocCardSupport.setChecked(socCardSupport)
        self.grpCardRbSettings.setEnabled(socCardSupport)
        self.grpCardReaderSettings.setEnabled(socCardSupport)
        self.chkDefaultClientSearchUsingSocCard.setEnabled(socCardSupport)
        self.chkCardReaderEmulation.setEnabled(socCardSupport)
        self.chkCardReaderEmulation.setChecked(forceBool(props.get('SocCard_Emulation', False)))
        self.chkDefaultClientSearchUsingSocCard.setChecked(forceBool(props.get('SocCard_SetAsDefaultSearch', False)))
        self.sbPortNumber.setValue(forceInt(props.get('SocCard_PortNumber', 0)))
        self.sbDevId.setValue(forceInt(props.get('SocCard_DevId', 0)))
        self.sbIssBSC0.setValue(forceInt(props.get('SocCard_IssBSC0', 0)))
        self.sbIssBSC1.setValue(forceInt(props.get('SocCard_IssBSC1', 0)))
        self.sbIssBSC2.setValue(forceInt(props.get('SocCard_IssBSC2', 0)))
        self.sbIssBSC3.setValue(forceInt(props.get('SocCard_IssBSC3', 0)))
        self.sbIssBSC4.setValue(forceInt(props.get('SocCard_IssBSC4', 0)))
        self.sbIssBSC5.setValue(forceInt(props.get('SocCard_IssBSC5', 0)))
        self.edtOperatorId.setText(forceString(props.get('SocCard_OperatorId', '')))
        self.edtDocumentTypeRbFileName.setText(forceString(props.get('SocCard_rbDocumentTypeRbFileName', '')))
        self.edtClientBenefitRbFileName.setText(forceString(props.get('SocCard_rbClientBenefitRbFileName', '')))

        self.grpTFCheckPolicy.setChecked(forceBool(props.get('TFCheckPolicy', QtCore.QVariant())))
        self.edtTFCPUrl.setText(forceString(props.get('TFCPUrl', QtCore.QVariant())))
        self.edtTFCPLogin.setText(forceString(props.get('TFCPLogin', QtCore.QVariant())))
        self.edtTFCPPassword.setText(forceString(props.get('TFCPPassword', QtCore.QVariant())))
        self.chkLoadAttach.setChecked(forceBool(props.get('TFCPAttach', QtCore.QVariant())))

        self.grpAttach.setChecked(forceBool(props.get('AttachCheckPolicy', QtCore.QVariant())))
        self.edtAttachUrl.setText(forceString(props.get('AttachUrl', QtCore.QVariant())))
        self.edtAttachLogin.setText(forceString(props.get('AttachLogin', QtCore.QVariant())))
        self.edtAttachPassword.setText(forceString(props.get('AttachPassword', QtCore.QVariant())))
        self.chkTransmitAttachData.setChecked(forceBool(props.get('TransmitAttachData', QtCore.QVariant())))
        self.chkDebugSoapAttach.setChecked(forceBool(props.get('DebugSoapAttach', QtCore.QVariant())))

        self.grpKzCheckIIN.setChecked(forceBool(props.get('IINCheckPolicy', QtCore.QVariant())))
        self.edtIINUrl.setText(forceString(props.get('IINUrl', QtCore.QVariant())))
        self.edtIINLogin.setText(forceString(props.get('IINLogin', QtCore.QVariant())))
        self.edtIINPassword.setText(forceString(props.get('IINPassword', QtCore.QVariant())))

        self.grpMIP.setChecked(forceBool(props.get('MIP', False)))
        self.edtMIPUrl.setText(forceString(props.get('MIPUrl', 'http://127.0.0.1:2116/MIPWinSrv/')))
        self.edtMIPContext.setText(forceString(props.get('MIPContext', 'http://127.0.0.1:2116/WSMCC/')))
        self.uekDirectAccess.setChecked(forceBool(props.get('UEKDirect', False)) and (os.name == 'nt'))
        self.uekDirectAccess.setEnabled(os.name == 'nt')

        self.grpEgisz.setChecked(forceBool(props.get('EGISZ', False)))
        self.edtEgiszAddress.setText(forceString(props.get('EGISZAddress', '')))

        self.grpUseDiaReg.setChecked(forceBool(props.get('UseDiaReg', False)))
        self.edtDiaRegAddress.setText(forceString(props.get('DiaRegAddress', '')))
        self.edtDiaRegUserName.setText(forceString(props.get('DiaRegUserName', '')))
        encPass = forceString(props.get('DiaRegPassword', ''))
        if encPass:
            self.edtDiaRegPassword.setText(decryptPassword(encPass))
        else:
            self.edtDiaRegPassword.setText('')

        self.edtDaysAmountToShowBefore.setValue(forceInt(props.get('DeferredDaysBefore', QtCore.QVariant(0))))
        self.edtDaysAmountToShowAfter.setValue(forceInt(props.get('DeferredDaysAfter', QtCore.QVariant(0))))
        self.chkDefaultMaxDateByAttach.setChecked(forceBool(props.get('DeferredMaxDateByAttach', False)))
        self.chkHideFinishedInDeferredQueue.setChecked(forceBool(props.get('HideFinishedDeferred', False)))

        self.grpBarCodeReader.setChecked(forceBool(props.get('BarCodeReaderEnable', False)))
        self.cmbBarCodeReader.setEditText(forceString(props.get('BarCodeReaderName', '\\\\.\\COM4')))

        self.edtAverageDuration.setValue(
            forceInt(props.get('averageDuration', QtCore.QVariant(DefaultAverageDuration))))
        self.cmbCheckDiagChange.setCurrentIndex(forceInt(props.get('checkDiagChange', QtCore.QVariant())))
        self.cmbCheckActionChange.setCurrentIndex(forceInt(props.get('checkActionChange', QtCore.QVariant())))
        self.cmbTempInvalidDoctype.setCode(forceString(props.get('tempInvalidDoctype', QtCore.QVariant())))
        self.cmbTempInvalidReason.setCode(forceString(props.get('tempInvalidReason', QtCore.QVariant())))
        self.edtTemplateDir.setText(forceString(props.get('templateDir', QtCore.QVariant(QtGui.qApp.getTemplateDir()))))
        iPrinter = self.cmbLabelPrinter.findText(forceString(props.get('labelPrinter', QtCore.QVariant())))
        self.cmbLabelPrinter.setCurrentIndex(iPrinter)
        self.cmbDoubleClickQueuePerson.setCurrentIndex(forceInt(props.get('doubleClickQueuePerson', QtCore.QVariant())))
        self.cmbQueuing.setCurrentIndex(forceInt(props.get('doubleClickQueuing', QtCore.QVariant())))
        self.cmbDoubleClickQueueClient.setCurrentIndex(forceInt(props.get('doubleClickQueueClient', QtCore.QVariant())))
        self.cmbDoubleClickQueueFreeOrder.setCurrentIndex(
            forceInt(props.get('doubleClickQueueFreeOrder', QtCore.QVariant())))
        self.chkAmbulanceUserCheckable.setChecked(forceBool(props.get('ambulanceUserCheckable', QtCore.QVariant())))
        self.cmbF025DefaultPrimacy.setCurrentIndex(forceInt(props.get('f025DefaultPrimacy', QtCore.QVariant())))
        self.chkAutoPrimacy.setChecked(forceBool(props.get('autoPrimacy', QtCore.QVariant())))
        self.f025PrimacySync()
        self.chkAddressOnlyByKLADR.setChecked(forceBool(props.get('addressOnlyByKLADR', QtCore.QVariant())))
        self.chkHighlightRedDate.setChecked(forceBool(props.get('highlightRedDate', QtCore.QVariant())))
        self.chkHighlightInvalidDate.setChecked(forceBool(props.get('highlightInvalidDate', QtCore.QVariant())))
        self.edtDocumentEditor.setText(forceString(props.get('documentEditor', '')))
        self.edtExtGenRep.setText(forceString(props.get('extGenRep', '')))
        self.edtCachBox.setText(forceString(props.get('cashBox', '')))
        self.edtExaroEditor.setText(forceString(props.get('exaroEditor', '')))
        self.edtExtArchiver.setText(forceString(props.get('extArchiver', '')))
        self.edtDicomViewerAddress.setText(forceString(props.get('dicomViewerAddress', '')))
        self.edtLISAddress.setText(forceString(props.get('LISAddress', '')))
        self.edtBrowserPath.setText(forceString(props.get('browserPath', '')))
        self.edtTimeRangeColors.setText(forceString(props.get('hospitalBedsTimeRangeColors', '')))
        self.chkUseCounterInContracts.setChecked(forceBool(props.get('useCounterInContracts', False)))
        self.chkUseCounterInAccounts.setChecked(forceBool(props.get('useCounterInAccounts', False)))
        self.chkShowVisitDateInRegistry.setChecked(forceBool(props.get('showVisitDateInRegistry', False)))
        self.chkGroupPrintWithutDialog.setChecked(forceBool(props.get('groupPrintWithoutDialog', False)))

        self.cmbHospitalizationDefaultEventType.setValue(forceRef(props.get('hospitalizationDefaultEventTypeId', None)))

        self.sbCompleterReduceIdleTimeout.setValue(forceInt(props.get('completerReduceIdleTimeout', 3)))
        self.sbCompleterReduceCharCount.setValue(forceInt(props.get('completerReduceCharCount', 3)))
        self.chkShowHospitalisation.setChecked(forceBool(props.get('showHospitalisation', False)))

        self.grpRecipesExchange.setChecked(forceBool(props.get('recipesExchangeEnabled', False)))
        self.edtRecipesExchangeUrl.setText(forceString(props.get('recipesExchangeUrl', '')))
        self.chkRecipesLog.setChecked(forceBool(props.get('recipesLog', False)))
        self.edtRecipesExchangeClientId.setText(forceString(props.get('recipesExchangeClientId', '')))
        # i3022
        self.chkDefaultSubdivision.setChecked(forceBool(props.get('defaultSubdivision', False)))

        self.cmbPersonSyncService.setCurrentIndex(forceInt(props.get('personSyncService', 0)))
        self.edtPersonSyncUrl.setText(forceString(props.get('personSyncUrl', '')))
        self.edtPersonSyncLogin.setText(forceString(props.get('personSyncLogin', '')))
        self.edtPersonSyncPassword.setText(forceString(props.get('personSyncPassword', '')))

        self.grpReferral.setChecked(forceBool(props.get('referralService', '')))
        self.edtRefUrl.setText(forceString(props.get('referralServiceUrl', '')))
        self.edtRefUser.setText(forceString(props.get('referralServiceUser', '')))
        self.edtRefPassword.setText(forceString(props.get('referralServicePassword', '')))

        # i2340
        self.grpEpoms.setChecked(forceBool(props.get('EPOMS', False)))
        self.cmbScardName.setCurrentIndex(self.cmbScardName.findText(forceString(props.get('cardReader', ''))))
        # self.cmbScardName.addItem(forceString(props.get('cardReader', '')))

        self.chkAddNotes.setChecked(forceBool(props.get('addNotes', False)))

        self.chkLinkingPerson.setChecked(forceBool(props.get('linkingPerson', False)))

        self.chkPrintPreview.setChecked(forceBool(props.get('printPreview', False)))

        # i3503
        self.chkEpircisModule.setChecked(forceBool(props.get('enableEpircisModule', False)))
        self.edtEpircisModule.setText(forceString(props.get('epircisModuleAddress', '')))

        # i3313
        self.chkEnableSocLab.setChecked(forceBool(props.get('enableSocLab', False)))
        self.edtSocLabAddress.setText(forceString(props.get('socLabAddress', '')))
        self.edtSocLabPort.setText(forceString(props.get('socLabPort', '')))
        self.edtSocLabLog.setText(forceString(props.get('socLabLog', '')))
        self.edtSocLabPass.setText(forceString(props.get('socLabPass', '')))

        self.grpAlfalab.setChecked(forceBool(props.get('alfalabEnabled', False)))
        self.edtAlfalabHost.setText(forceString(props.get('alfalabHost', '')))
        self.edtAlfalabSender.setText(forceString(props.get('alfalabSender', '')))
        self.edtAlfalabReceiver.setText(forceString(props.get('alfalabReceiver', '')))
        self.edtAlfalabPassword.setText(forceString(props.get('alfalabPassword', '')))

        # ССМП i3617
        self.grpSSMP.setChecked(forceBool(props.get('smpService', False)))
        self.edtSSMPAddress.setText(forceString(props.get('smpAddress', '')))
        self.chkShowErrorMessages.setChecked(forceBool(props.get('showErrorMessages', False)))

        # Управление очередями. Нетрика. i3511
        self.chkUOService.setChecked(forceBool(props.get('UOService', False)))
        self.edtUOServiceAddress.setText(forceString(props.get('UOServiceAddress', '')))
        self.edtUOServiceToken.setText(forceString(props.get('UOServiceToken', '')))

        # Городской реестр карт маршрутизации (ГРКМ). i3838
        self.grpGrkm.setChecked(forceBool(props.get('GRKMService', False)))
        self.edtGrkmAddress.setText(forceString(props.get('GRKMServiceAddress', '')))
        self.edtGrkmUser.setText(forceString(props.get('GRKMServiceUser', '')))
        self.edtGrkmPassword.setText(forceString(props.get('GRKMServicePassword'  '')))
        self.cmbGrkmLevel.setCurrentIndex(forceInt(props.get('GRKMServiceLevel', 0)))

        # Личный кабинет
        self.grpPersCab.setChecked(forceBool(props.get('PersCabService', False)))
        self.edtHostPersCab.setText(forceString(props.get('HostPersCabService', '')))

        # Листы нетрудоспособности
        self.grpLNService.setChecked(forceBool(props.get('LNService', False)))
        self.edtLNAddress.setText(forceString(props.get('LNAddress', '')))

        self.cmbDefaultPrintFont.setCurrentFont(QtGui.QFont(props.get('printFontFamily', 'Times New Roman')))
        self.edtDefaultPrintFontSize.setValue(forceInt(props.get('printFontFamilySize', 11)))

        self.chkDisableSumPricesCol.setChecked(forceBool(props.get('DisableSumPricesCol', True)))

        self.edtIEMKCaseURL.setText(forceString(props.get('edtCaseURL', '')))
        self.edtIEMKPixURL.setText(forceString(props.get('edtPixURL', '')))
        self.edtIEMKGUID.setText(forceString(props.get('edtGUID')))

        self.chkJobsOperatingLabOrders.setChecked(forceBool(props.get('JobsOperatingLabOrders', False)))
        self.chkAutoJobTicketEditing.setChecked(forceBool(props.get('autoJobTicketEditing', False)))

    def props(self):
        global DefaultSMTPPort

        result = {}
        result['orgId'] = toVariant(self.cmbOrganisation.value())
        result['orgStructureId'] = toVariant(self.cmbOrgStructure.value())
        result['filterPaymentByOrgStructure'] = toVariant(
            1 if self.chkFilterPaymentByOrgStructure.isChecked() else 0)
        result['orgStructurePriorityForAddActions'] = toVariant(
            1 if self.chkOrgStructurePriorityForAddActions.isChecked() else 0)
        result['defaultKLADR'] = toVariant(self.cmbDefaultCity.code())
        result['provinceKLADR'] = toVariant(self.cmbProvince.code())
        result['SMTPServer'] = toVariant(forceStringEx(self.edtSMTPServer.text()))
        try:
            port = int(forceStringEx(self.edtSMTPPort.text()))
        except ValueError:
            port = 25
        result['SMTPPort'] = toVariant(port if port > 0 else DefaultSMTPPort)
        result['mailAddress'] = toVariant(forceStringEx(self.edtMailAddress.text()))
        result['SMTPAuthentification'] = toVariant(self.chkSMTPAuthentification.isChecked())
        result['SMTPLogin'] = toVariant(forceStringEx(self.edtSMTPLogin.text()))
        result['SMTPPassword'] = toVariant(forceStringEx(self.edtSMTPPassword.text()))

        result['EIS_driverName'] = toVariant(forceStringEx(self.cmbDriverName.currentText()))
        result['EIS_serverName'] = toVariant(forceStringEx(self.edtServerName.text()))
        result['EIS_serverPort'] = toVariant(forceInt(self.edtServerPort.value()))
        result['EIS_databaseName'] = toVariant(forceStringEx(self.edtDatabaseName.text()))
        result['EIS_userName'] = toVariant(forceStringEx(self.edtUserName.text()))
        result['EIS_password'] = toVariant(forceStringEx(self.edtPassword.text()))
        result['EIS_codepage'] = toVariant(forceStringEx(self.edtCodepage.text()))

        result['SocCard_SupportEnabled'] = toVariant(self.chkEnableSocCardSupport.isChecked())
        result['SocCard_Emulation'] = toVariant(self.chkCardReaderEmulation.isChecked())
        result['SocCard_SetAsDefaultSearch'] = toVariant(self.chkDefaultClientSearchUsingSocCard.isChecked())
        result['SocCard_PortNumber'] = toVariant(self.sbPortNumber.value())
        result['SocCard_DevId'] = toVariant(self.sbDevId.value())
        result['SocCard_IssBSC0'] = toVariant(self.sbIssBSC0.value())
        result['SocCard_IssBSC1'] = toVariant(self.sbIssBSC1.value())
        result['SocCard_IssBSC2'] = toVariant(self.sbIssBSC2.value())
        result['SocCard_IssBSC3'] = toVariant(self.sbIssBSC3.value())
        result['SocCard_IssBSC4'] = toVariant(self.sbIssBSC4.value())
        result['SocCard_IssBSC5'] = toVariant(self.sbIssBSC5.value())
        result['SocCard_OperatorId'] = toVariant(self.edtOperatorId.text())
        result['SocCard_rbDocumentTypeRbFileName'] = toVariant(self.edtDocumentTypeRbFileName.text())
        result['SocCard_rbClientBenefitRbFileName'] = toVariant(self.edtClientBenefitRbFileName.text())

        result['TFCheckPolicy'] = toVariant(int(self.grpTFCheckPolicy.isChecked()))
        result['TFCPUrl'] = toVariant(self.edtTFCPUrl.text())
        result['TFCPLogin'] = toVariant(self.edtTFCPLogin.text())
        result['TFCPPassword'] = toVariant(self.edtTFCPPassword.text())
        result['TFCPAttach'] = toVariant(self.chkLoadAttach.isChecked())

        result['AttachCheckPolicy'] = toVariant(int(self.grpAttach.isChecked()))
        result['AttachUrl'] = toVariant(self.edtAttachUrl.text())
        result['AttachLogin'] = toVariant(self.edtAttachLogin.text())
        result['AttachPassword'] = toVariant(self.edtAttachPassword.text())
        result['TransmitAttachData'] = toVariant(self.chkTransmitAttachData.isChecked())
        result['DebugSoapAttach'] = toVariant(self.chkDebugSoapAttach.isChecked())

        result['IINCheckPolicy'] = toVariant(int(self.grpKzCheckIIN.isChecked()))
        result['IINUrl'] = toVariant(self.edtIINUrl.text())
        result['IINLogin'] = toVariant(self.edtIINLogin.text())
        result['IINPassword'] = toVariant(self.edtIINPassword.text())

        result['MIP'] = toVariant(int(self.grpMIP.isChecked()))
        result['MIPUrl'] = toVariant(self.edtMIPUrl.text())
        result['MIPContext'] = toVariant(self.edtMIPContext.text())

        result['UEKDirect'] = toVariant(int(self.uekDirectAccess.isChecked()))

        result['EGISZ'] = toVariant(int(self.grpEgisz.isChecked()))
        result['EGISZAddress'] = toVariant(self.edtEgiszAddress.text())

        result['UseDiaReg'] = toVariant(int(self.grpUseDiaReg.isChecked()))
        result['DiaRegAddress'] = toVariant(self.edtDiaRegAddress.text())
        result['DiaRegUserName'] = toVariant(self.edtDiaRegUserName.text())
        result['DiaRegPassword'] = toVariant(encryptPassword(forceString(self.edtDiaRegPassword.text())))

        result['DeferredDaysBefore'] = toVariant(self.edtDaysAmountToShowBefore.value())
        result['DeferredDaysAfter'] = toVariant(self.edtDaysAmountToShowAfter.value())
        result['DeferredMaxDateByAttach'] = toVariant(self.chkDefaultMaxDateByAttach.isChecked())
        result['HideFinishedDeferred'] = toVariant(self.chkHideFinishedInDeferredQueue.isChecked())

        result['BarCodeReaderEnable'] = toVariant(int(self.grpBarCodeReader.isChecked()))
        result['BarCodeReaderName'] = toVariant(self.cmbBarCodeReader.currentText())

        result['averageDuration'] = toVariant(self.edtAverageDuration.value())
        result['checkDiagChange'] = toVariant(self.cmbCheckDiagChange.currentIndex())
        result['checkActionChange'] = toVariant(self.cmbCheckActionChange.currentIndex())
        result['tempInvalidDoctype'] = toVariant(self.cmbTempInvalidDoctype.code())
        result['tempInvalidReason'] = toVariant(self.cmbTempInvalidReason.code())

        result['templateDir'] = toVariant(self.edtTemplateDir.text())
        result['labelPrinter'] = toVariant(self.cmbLabelPrinter.currentText())

        result['doubleClickQueuePerson'] = toVariant(self.cmbDoubleClickQueuePerson.currentIndex())
        result['doubleClickQueuing'] = toVariant(self.cmbQueuing.currentIndex())
        result['doubleClickQueueClient'] = toVariant(self.cmbDoubleClickQueueClient.currentIndex())
        result['doubleClickQueueFreeOrder'] = toVariant(self.cmbDoubleClickQueueFreeOrder.currentIndex())

        result['ambulanceUserCheckable'] = toVariant(int(self.chkAmbulanceUserCheckable.isChecked()))
        result['f025DefaultPrimacy'] = toVariant(self.cmbF025DefaultPrimacy.currentIndex())

        result['autoPrimacy'] = toVariant(int(self.chkAutoPrimacy.isChecked()))

        result['addressOnlyByKLADR'] = toVariant(int(self.chkAddressOnlyByKLADR.isChecked()))
        result['highlightRedDate'] = toVariant(int(self.chkHighlightRedDate.isChecked()))
        result['highlightInvalidDate'] = toVariant(int(self.chkHighlightInvalidDate.isChecked()))
        result['documentEditor'] = toVariant(self.edtDocumentEditor.text())
        result['extGenRep'] = toVariant(self.edtExtGenRep.text())
        result['cashBox'] = toVariant(self.edtCachBox.text())
        result['exaroEditor'] = toVariant(self.edtExaroEditor.text())
        result['extArchiver'] = toVariant(self.edtExtArchiver.text())
        result['dicomViewerAddress'] = toVariant(self.edtDicomViewerAddress.text())
        result['LISAddress'] = toVariant(self.edtLISAddress.text())
        result['browserPath'] = toVariant(self.edtBrowserPath.text())
        result['hospitalBedsTimeRangeColors'] = toVariant(self.edtTimeRangeColors.text())
        result['useCounterInContracts'] = toVariant(self.chkUseCounterInContracts.isChecked())
        result['useCounterInAccounts'] = toVariant(self.chkUseCounterInAccounts.isChecked())
        result['showVisitDateInRegistry'] = toVariant(self.chkShowVisitDateInRegistry.isChecked())
        result['groupPrintWithoutDialog'] = toVariant(self.chkGroupPrintWithutDialog.isChecked())

        result['hospitalizationDefaultEventTypeId'] = toVariant(self.cmbHospitalizationDefaultEventType.value())

        result['completerReduceIdleTimeout'] = toVariant(self.sbCompleterReduceIdleTimeout.value())
        result['completerReduceCharCount'] = toVariant(self.sbCompleterReduceCharCount.value())
        result['showHospitalisation'] = toVariant(self.chkShowHospitalisation.isChecked())

        result['recipesExchangeUrl'] = toVariant(self.edtRecipesExchangeUrl.text())
        result['recipesExchangeClientId'] = toVariant(self.edtRecipesExchangeClientId.text())
        result['recipesLog'] = toVariant(self.chkRecipesLog.isChecked())
        result['recipesExchangeEnabled'] = toVariant(self.grpRecipesExchange.isChecked())

        # i3022
        result['defaultSubdivision'] = toVariant(self.chkDefaultSubdivision.isChecked())

        result['personSyncUrl'] = toVariant(self.edtPersonSyncUrl.text())
        result['personSyncLogin'] = toVariant(self.edtPersonSyncLogin.text())
        result['personSyncPassword'] = toVariant(self.edtPersonSyncPassword.text())
        result['personSyncService'] = toVariant(self.cmbPersonSyncService.currentIndex())

        # i3055
        result['referralService'] = toVariant(int(self.grpReferral.isChecked()))
        result['referralServiceUrl'] = toVariant(self.edtRefUrl.text())
        result['referralServiceUser'] = toVariant(self.edtRefUser.text())
        result['referralServicePassword'] = toVariant(self.edtRefPassword.text())

        # ЭПОМС
        result['EPOMS'] = toVariant(self.grpEpoms.isChecked())
        result['cardReader'] = toVariant(self.cmbScardName.currentText())

        # Добавление жалоб в примечания
        result['addNotes'] = toVariant(self.chkAddNotes.isChecked())

        result['linkingPerson'] = toVariant(self.chkLinkingPerson.isChecked())

        result['printPreview'] = toVariant(self.chkPrintPreview.isChecked())

        # i3503
        result['enableEpircisModule'] = toVariant(self.chkEpircisModule.isChecked())
        result['epircisModuleAddress'] = toVariant(self.edtEpircisModule.text())

        # i3313
        result['enableSocLab'] = toVariant(self.chkEnableSocLab.isChecked())
        result['socLabAddress'] = toVariant(self.edtSocLabAddress.text())
        result['socLabPort'] = toVariant(self.edtSocLabPort.text())
        result['socLabLog'] = toVariant(self.edtSocLabLog.text())
        result['socLabPass'] = toVariant(self.edtSocLabPass.text())

        result['alfalabEnabled'] = toVariant(self.grpAlfalab.isChecked())
        result['alfalabHost'] = toVariant(self.edtAlfalabHost.text())
        result['alfalabSender'] = toVariant(self.edtAlfalabSender.text())
        result['alfalabReceiver'] = toVariant(self.edtAlfalabReceiver.text())
        result['alfalabPassword'] = toVariant(self.edtAlfalabPassword.text())

        result['smpService'] = toVariant(self.grpSSMP.isChecked())
        result['smpAddress'] = toVariant(self.edtSSMPAddress.text())
        result['showErrorMessages'] = toVariant(self.chkShowErrorMessages.isChecked())

        result['UOService'] = toVariant(self.chkUOService.isChecked())
        result['UOServiceAddress'] = toVariant(self.edtUOServiceAddress.text())
        result['UOServiceToken'] = toVariant(self.edtUOServiceToken.text())

        result['GRKMService'] = toVariant(self.grpGrkm.isChecked())
        result['GRKMServiceAddress'] = toVariant(self.edtGrkmAddress.text())
        result['GRKMServiceUser'] = toVariant(self.edtGrkmUser.text())
        result['GRKMServicePassword'] = toVariant(self.edtGrkmPassword.text())
        result['GRKMServiceLevel'] = toVariant(self.cmbGrkmLevel.currentIndex())

        result['PersCabService'] = toVariant(self.grpPersCab.isChecked())
        result['HostPersCabService'] = toVariant((self.edtHostPersCab.text()))

        result['LNService'] = toVariant(self.grpLNService.isChecked())
        result['LNAddress'] = toVariant(self.edtLNAddress.text())

        result['printFontFamily'] = toVariant(self.cmbDefaultPrintFont.currentFont().family())
        result['printFontFamilySize'] = toVariant(self.edtDefaultPrintFontSize.value())

        result['DisableSumPricesCol'] = toVariant(self.chkDisableSumPricesCol.isChecked())

        result['edtCaseURL'] = toVariant(self.edtIEMKCaseURL.text())
        result['edtPixURL'] = toVariant(self.edtIEMKPixURL.text())
        result['edtGUID'] = toVariant(self.edtIEMKGUID.text())

        result['JobsOperatingLabOrders'] = toVariant(self.chkJobsOperatingLabOrders.isChecked())
        result['autoJobTicketEditing'] = toVariant(self.chkAutoJobTicketEditing.isChecked())

        return result

    @QtCore.pyqtSlot()
    def on_uekDirectAccess_clicked(self):
        if isPython27() and os.name == 'nt':
            self.uekDirectAccess.setChecked(self.uekDirectAccess.isChecked())
            self.grpMIP.setChecked(self.grpMIP.isChecked() and not self.uekDirectAccess.isChecked())
        else:
            self.uekDirectAccess.setChecked(False)
            self.grpMIP.setChecked(False)

    @QtCore.pyqtSlot()
    def on_grpMIP_clicked(self):
        self.grpMIP.setChecked(self.grpMIP.isChecked())
        if isPython27():
            self.uekDirectAccess.setChecked(
                not self.grpMIP.isChecked() and self.uekDirectAccess.isChecked() and os.name == 'nt')
        else:
            self.uekDirectAccess.setChecked(False)

    @QtCore.pyqtSlot()
    def on_btnMIPTest_clicked(self):
        try:
            mipSrv = CMIPWinSrv(forceStringEx(self.edtMIPUrl.text()))
            res = mipSrv.ReadContext()
            contextSrv = CWSMCC(forceStringEx(self.edtMIPContext.text()))
            contextSrv.ReadContext(mipSrv.Guid)
            message = u'Считыватель работает нормально.'
        except:
            message = u'Ошибка чтения машиночитаемого идентификатора пациента.'

        QtGui.QMessageBox.information(self, u'Проверка обращения к сервису МИП', message, QtGui.QMessageBox.Ok,
                                      QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot(int)
    def on_cmbOrganisation_currentIndexChanged(self, index):
        orgId = self.cmbOrganisation.value()
        self.cmbOrgStructure.setOrgId(orgId)

    @QtCore.pyqtSlot()
    def on_btnSelectOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrganisation.value(), False)
        self.cmbOrganisation.update()
        if orgId:
            self.cmbOrganisation.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbDefaultCity_currentIndexChanged(self):
        cityKLADRCode = self.cmbDefaultCity.code()
        provinceKLADRCode = getProvinceKLADRCode(cityKLADRCode)
        self.cmbProvince.setCode(provinceKLADRCode)

    @QtCore.pyqtSlot(bool)
    def on_chkSMTPAuthentification_clicked(self, checked):
        if checked and self.edtSMTPLogin.text().isEmpty():
            self.edtMailAddress.text()
            match = re.compile(r'''^(?:.*\s+)?([^\s]+)@''').match(forceString(self.edtMailAddress.text()))
            if match:
                self.edtSMTPLogin.setText(match.group(1))

    @QtCore.pyqtSlot()
    def on_btnEisTest_clicked(self):
        try:
            EIS_db = QtGui.qApp.EIS_db
            if not EIS_db:
                EIS_dbDriverName = forceStringEx(self.cmbDriverName.currentText())
                EIS_dbServerName = forceStringEx(self.edtServerName.text())
                EIS_dbServerPort = forceInt(self.edtServerPort.value())
                EIS_dbDatabaseName = forceStringEx(self.edtDatabaseName.text())
                EIS_dbUserName = forceStringEx(self.edtUserName.text())
                EIS_dbPassword = forceStringEx(self.edtPassword.text())
                EIS_dbCodepage = forceStringEx(self.edtCodepage.text())
                EIS_db = database.connectDataBase(EIS_dbDriverName,
                                                  EIS_dbServerName,
                                                  EIS_dbServerPort,
                                                  EIS_dbDatabaseName,
                                                  EIS_dbUserName,
                                                  EIS_dbPassword,
                                                  'EIS',
                                                  LC_CTYPE=EIS_dbCodepage)
                QtGui.qApp.EIS_db = EIS_db
            TARIFF_MONTH = EIS_db.getRecordEx('TARIFF_MONTH', '*', '')
            ID_TARIFF_MONTH = forceString(TARIFF_MONTH.value('ID_TARIFF_MONTH'))
            TARIFF_MONTH_BEG = forceString(TARIFF_MONTH.value('TARIFF_MONTH_BEG').toDate())
            TARIFF_MONTH_END = forceString(TARIFF_MONTH.value('TARIFF_MONTH_END').toDate())
            MU_IDENT = EIS_db.getRecordEx('MU_IDENT', 'ID_LPU')
            ID_LPU = forceInt(MU_IDENT.value('ID_LPU')) if MU_IDENT else None
            message = u'Соединение успешно!\nтарифный месяц: %s (%s-%s)\nИдентификатор ЛПУ в ЕИС ОМС: %s' % (
            ID_TARIFF_MONTH, TARIFF_MONTH_BEG, TARIFF_MONTH_END, ID_LPU)
            QtGui.qApp.EIS_db.close()
            QtGui.qApp.EIS_db = None
        except Exception as e:
            QtGui.qApp.logCurrentException()
            if QtGui.qApp.EIS_db:
                QtGui.qApp.EIS_db.close()
                QtGui.qApp.EIS_db = None
            message = u'Установить соединение не удалось' + u'\n' + unicode(e)
        QtGui.QMessageBox.information(self, u'Проверка обращения к серверу ЕИС',
                                      message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_btnSelectTemplateDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(
            self, u'Укажите директорию с шаблонами документов', self.edtTemplateDir.text())
        if dir:
            self.edtTemplateDir.setText(QtCore.QDir.toNativeSeparators(dir))

    @QtCore.pyqtSlot()
    def on_btnSelectDocumentEditor_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите исполнимый файл редактора документов',
            self.edtDocumentEditor.text(), u'Исполнимые файлы (*)'))
        if fileName:
            self.edtDocumentEditor.setText(QtCore.QDir.toNativeSeparators(fileName))

    @QtCore.pyqtSlot()
    def on_btnSelectExtGenRep_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите исполнимый файл генератора отчетов',
            self.edtExtGenRep.text(), u'Исполнимые файлы (*)'))

        if fileName:
            self.edtExtGenRep.setText(QtCore.QDir.toNativeSeparators(fileName))

    @QtCore.pyqtSlot()
    def on_btnSelectExtArchiver_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите исполнимый файл архиватора',
            self.edtExtArchiver.text(), u'Исполнимые файлы (*)'))

        if fileName:
            self.edtExtArchiver.setText(QtCore.QDir.toNativeSeparators(fileName))

    @QtCore.pyqtSlot()
    def on_btnSelectExaroEditor_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите исполнимый файл редактора отчетов Exaro',
            self.edtExaroEditor.text(), u'Исполнимые файлы (*)'))

        if fileName:
            self.edtExaroEditor.setText(QtCore.QDir.toNativeSeparators(fileName))

    @QtCore.pyqtSlot(bool)
    def on_chkEnableSocCardSupport_clicked(self, checked):
        self.grpCardRbSettings.setEnabled(checked)
        self.grpCardReaderSettings.setEnabled(checked)
        self.chkDefaultClientSearchUsingSocCard.setEnabled(checked)
        self.chkCardReaderEmulation.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_btnSelectClientBenefitRbFileName_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл со справочниками типов льгот',
            self.edtClientBenefitRbFileName.text(), u'Файлы XML (*.xml)'))

        if fileName:
            self.edtClientBenefitRbFileName.setText(QtCore.QDir.toNativeSeparators(fileName))

    @QtCore.pyqtSlot()
    def on_btnSelectDocumentTypeRbFileName_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл со справочниками типов документов',
            self.edtDocumentTypeRbFileName.text(), u'Файлы XML (*.xml)'))

        if fileName:
            self.edtDocumentTypeRbFileName.setText(QtCore.QDir.toNativeSeparators(fileName))

    @QtCore.pyqtSlot()
    def on_btnSocCardTest_clicked(self):
        prefs = QtGui.qApp.preferences.appPrefs
        if self.chkCardReaderEmulation.isChecked():
            from Registry.CardReader import CCardReaderEmulator
            cardReader = CCardReaderEmulator()
        else:
            from Registry.CardReader import CCardReader
            cardReader = CCardReader()

        nPortNo = self.sbPortNumber.value()
        diDevId = self.sbDevId.value()
        listIssBSC = []

        for i in range(0, 6):
            listIssBSC.append(getattr(self, 'sbIssBSC%d' % i).value())

        szOperatorId = forceString(self.edtOperatorId.text())

        initOk = cardReader.init(nPortNo, diDevId, listIssBSC, szOperatorId)
        rc = cardReader.rc()
        cardIn = cardReader.checkCardType()
        from Registry.CardReader import loadDocumentTypeRb, loadBenefitTypeRb
        docTypeRb = (loadDocumentTypeRb(self, forceString(self.edtDocumentTypeRbFileName.text())) != {})
        benefitTypeRb = (loadBenefitTypeRb(self, forceString(self.edtClientBenefitRbFileName.text())) != {})

        message = u'<h4>Результат тестирования: </h4>\n' \
                  u'Инициализация: <b>%s</b><br>' \
                  u'Наличие карты: <b>%s</b><br><br>' \
                  u'Справочник типов документов: <b>%s</b><br>' \
                  u'Справочник типов льгот: <b>%s</b><br><br>' \
                  u'Параметры соединения:<table>' \
                  u'<tr><td>Номер порта:</td><td><b>%d</b></td></tr>' \
                  u'<tr><td>Идентификатор устройства:</td><td><b>%d</b></td></tr>' \
                  u'<tr><td>Код банка:</td><td><b>%.2d%.2d%.2d%.2d%.2d%.2d</b></td></tr>' \
                  u'<tr><td>Идентификатор оператора:</td><td><b>%s</b></td></tr>' \
                  u'<tr><td>Ошибка:</td><td><b>%s (код %d)</b></td></tr></table>' % \
                  (u'успешно' if initOk else u'ошибка', u'есть' if cardIn else u'отсутствует',
                   u'прочитан' if docTypeRb else u'ошибка', u'прочитан' if benefitTypeRb else u'ошибка',
                   nPortNo, diDevId, listIssBSC[0], listIssBSC[1], listIssBSC[2], listIssBSC[3],
                   listIssBSC[4], listIssBSC[5], szOperatorId, cardReader.errorText(rc), rc)

        QtGui.QMessageBox.information(self, u'Проверка работы социальной карты',
                                      message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_btnTFCPTest_clicked(self):
        kladr = forceString(self.cmbDefaultCity.code())
        if not kladr:
            kladr = '7800000000000'
        servClass = CTF23IdentService if kladr.startswith('23') else CTF78IdentService
        service = servClass(forceString(self.edtTFCPUrl.text()),
                            forceString(self.edtTFCPLogin.text()),
                            forceString(self.edtTFCPPassword.text()))
        try:
            if kladr.startswith('23'):
                QtGui.qApp.callWithWaitCursor(self, service.getPort)
            else:
                QtGui.qApp.callWithWaitCursor(self, service.getSmoList)
            message = u'Соединение успешно'
        except:
            QtGui.qApp.logCurrentException()
            message = u'Соединение не удалось'

        QtGui.QMessageBox.information(self, u'Проверка соединения',
                                      message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_btnAttachTest_clicked(self):
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            connection = CR23LoginAccessService.createConnection(forceString(self.edtAttachUrl.text()))
            message = connection.makeTestConnect()

        except Exception, e:
            QtGui.qApp.logCurrentException()
            message = u'Соединение не удалось: %s' % forceString(e)

        finally:
            QtGui.QApplication.restoreOverrideCursor()

        QtGui.QMessageBox.information(self, u'Проверка соединения', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_btnAttachRegister_clicked(self):
        url = forceString(self.edtAttachUrl.text())
        username = forceString(self.edtAttachLogin.text())
        senderCode = username
        password = forceString(self.edtAttachPassword.text())
        oldPassword = forceString(self.edtAttachOldPassword.text()) or None
        isRegisterMultiple = self.chkAttachRegisterMultiple.isChecked()

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            connection = CR23LoginAccessService.getConnection(url)
            if isRegisterMultiple:
                message = connection.setLoginAccessMultiple(password)
            else:
                message = connection.setLoginAccess(username, password, senderCode, oldPassword)

        except Exception, e:
            # QtGui.qApp.logCurrentException()
            message = u'Соединение не удалось: %s' % forceString(e)

        finally:
            QtGui.QApplication.restoreOverrideCursor()

        QtGui.QMessageBox.information(self, u'Результаты', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_btnIINCheck_clicked(self):
        url = forceString(self.edtIINUrl.text())
        login = forceString(self.edtIINLogin.text())
        password = forceString(self.edtIINPassword.text())
        if url == u'' or login == u'' or password == u'':
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Пожалуйста, заполните все поля!', QtGui.QMessageBox.Ok)
        service = CR90IINService(login, password, url)
        res = service.postAuthorization()
        if res:
            message = u'Соединение прошло успешно'
        else:
            message = u'Соединение не удалось'
        QtGui.QMessageBox.information(self, u'Результаты', message, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblGlobal_doubleClicked(self, index):
        if QtGui.qApp.userHasAnyRight(['adm', 'setupGlobalPreferencesEdit']):
            item = self.tblGlobal.currentItem()
            currentValue = forceString(item.value('value'))
            note = forceString(item.value('note'))
            newValue, ok = QtGui.QInputDialog.getText(self,
                                                      u'Редактор',
                                                      u'Значение\n' + note,
                                                      QtGui.QLineEdit.Normal,
                                                      currentValue)
            if ok and unicode(newValue) != unicode(currentValue):
                item.setValue('value', QtCore.QVariant(newValue))
                if QtGui.qApp.db.updateRecord('GlobalPreferences', item):
                    QtGui.qApp.updateGlobalPreference(forceString(item.value('code')))
                self.refreshGlobalPreferences()

    def on_btnEQResetSettings_clicked(self):
        self.btnEQResetSettings.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_btnLNCheckService_clicked(self):
        if self.edtLNAddress.text():
            ex = LnService()
            if ex.pingService():
                QtGui.QMessageBox.information(self, u'Успех', u'Соединение установленно.')
            else:
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Не удалось установить соединение.')
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Введите адрес.')


# ########################################################
class CGlobalPreferencesModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Код', ['code'], 10))
        self.addColumn(CTextCol(u'Наименование', ['name'], 18))
        self.addColumn(CTextCol(u'Значение', ['value'], 10))
        self.loadField('note')
        self.setTable('GlobalPreferences')
