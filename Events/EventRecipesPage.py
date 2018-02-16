# -*- coding: utf-8 -*-

# ############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
import os
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QChar, QDateTime, QSize, QString, Qt
from PyQt4.QtGui import QDialog, QIcon, QMessageBox, QToolBar

from Events.EventRecipesDrugstore import CEventRecipesDrugstore
from Events.RecipeAnnulmentDialog import CRecipeAnnulmentDialog
from Events.RecipeEditDialog import CRecipeEditDialog
from Exchange.R23.recipes.RecipeService import CR23RecipeService
from Orgs.PersonInfo import CPersonInfo
from Registry.Utils import CClientInfo, CClientSocStatusInfoList, getClientInfo
from Ui_EventRecipesPage import Ui_EventRecipesPageWidget
from library.DialogBase import CConstructHelperMixin
from library.InDocTable import CBoolInDocTableCol, CDateTimeInDocTableCol, CEnumInDocTableCol, CInDocTableCol, CInDocTableModel, CRBInDocTableCol
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, getFirstPrintTemplate
from library.Recipe.RecipeInfo import CDrugRecipeInfo
from library.Recipe.Utils import getBookkeeperCode, getDocumentNumber, recipeStatusNames
from library.TableModel import CIntCol
from library.Utils import forceBool, forceInt, forceRef, forceString, getVal, toVariant
from library.crbcombobox import CRBComboBox


class CFastEventRecipesPage(QtGui.QWidget, CConstructHelperMixin, Ui_EventRecipesPageWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.eventId = None
        self.financeId = None
        self.personId = None
        self.clientId = None
        self.mkb = None
        self.characterId = None

        self.actAdd = QtGui.QAction(QIcon(':/new/prefix1/icons/new-icon.png'), u'Добавить', self)

        self.actAdd.setObjectName('actAdd')
        self.actEdit = QtGui.QAction(QIcon(':/new/prefix1/icons/edit-icon.png'), u'Изменить', self)
        self.actEdit.setObjectName('actEdit')
        self.actDuplicate = QtGui.QAction(QIcon(':/new/prefix1/icons/duplicate-icon.png'), u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actDelete = QtGui.QAction(QIcon(':/new/prefix1/icons/delete-icon.png'), u'Удалить', self)
        self.actDelete.setObjectName('actDelete')
        self.actPrint = QtGui.QAction(QIcon(':/new/prefix1/icons/print-icon.png'), u'Печать', self)
        self.actPrint.setObjectName('actPrint')
        self.actAnnul = QtGui.QAction(u'Изменить статус рецепта', self)
        self.actAnnul.setObjectName('actAnnul')
        self.actDrugstore = QtGui.QAction(u'Наличие ЛС в аптеках', self)
        self.actDrugstore.setObjectName('actDrugstore')
        self.setupUi(self)

        self.toolBar = QToolBar(self)
        self.toolBar.setIconSize(QSize(24, 24))
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.layout().insertWidget(0, self.toolBar)
        self.toolBar.addAction(self.actAdd)
        self.toolBar.addAction(self.actEdit)
        self.toolBar.addAction(self.actDelete)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actPrint)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actDrugstore)

        self.addModels('Items', CItemsModel(self))
        self.tblItems.setModel(self.modelItems)
        self.tblItems.setSelectionModel(self.selectionModelItems)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.connect(self.selectionModelItems, QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'), self.on_selectionModelItems_currentChanged)
        self.tblItems.createPopupMenu([self.actAnnul])
        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

        self.actEdit.setEnabled(False)
        self.actDelete.setEnabled(False)
        self.actPrint.setEnabled(False)

    def setupUiMini(self, Dialog):
        pass

    def preSetupUiMini(self):
        pass

    def preSetupUi(self):
        pass

    def postSetupUiMini(self):
        pass

    def postSetupUi(self):
        pass

    def popupMenuAboutToShow(self):
        currentItem = self.tblItems.currentIndex()
        # self.actEdit.setEnabled(currentItem.isValid())
        # self.actDelete.setEnabled(currentItem.isValid())
        self.actAnnul.setEnabled(currentItem.isValid())

    def setEventId(self, eventId, financeId, recFinalDiagnosis, clientId, personId):
        self.eventId = eventId
        self.financeId = financeId
        self.mkb = forceString(recFinalDiagnosis.value('MKB')) if recFinalDiagnosis else None
        self.characterId = forceRef(recFinalDiagnosis.value('character_id')) if recFinalDiagnosis else None
        self.clientId = clientId
        self.personId = personId
        self.loadData()

    def loadData(self):
        if self.eventId is not None:
            self.tblItems.model().loadItems(self.eventId)

    def saveData(self, eventId):
        self.eventId = eventId
        self.tblItems.model().saveItems(eventId)

    # TODO: mdldml: перенести все подобные действия в модель, а то некрасиво
    @QtCore.pyqtSlot()
    def on_actAdd_triggered(self):
        db = QtGui.qApp.db
        clientInfo = getClientInfo(self.clientId)
        if len(clientInfo.SNILS) == 0:
            QtGui.QMessageBox.warning(
                self,
                u'Внимание',
                u'У пациента не заполнен СНИЛС.\n'
                u'Укажите СНИЛС пациента в рег. карте.',
                QtGui.QMessageBox.Close
            )
            return
        if len(clientInfo.socStatuses) == 0:
            QtGui.QMessageBox.warning(self, u'Внимание', u'У пациента отсутствуют льготы.', QMessageBox.Close)
            return
        federalCode = forceString(db.translate('Person', 'id', self.personId, 'federalCode'))
        if len(federalCode) == 0:
            QtGui.QMessageBox.warning(self, u'Внимание', u'У ответственного за событие врача не указан федеральный код.', QMessageBox.Close)
            return

        record = self.tblItems.model().getEmptyRecord()
        record.setValue('dateTime', toVariant(QDateTime().currentDateTime()))
        try:
            record.setValue('percentage', toVariant(100))
            if self.mkb:
                record.setValue('mkb', toVariant(self.mkb))
            record.setValue('term', toVariant(2))
            record.setValue('printMnn', toVariant(1))

            context = CInfoContext()
            client, setPerson = self.getEventInfo(context)

            if len(client.socStatuses) == 0:
                raise Exception(u'В регистрационной карте не указаны льготы!')

            dlg = CRecipeEditDialog(self, client.socStatuses, client.id, setPerson.personId)
            dlg.setRecord(record)
            if dlg.exec_() == QDialog.Accepted:
                dlg.getRecord(record)
                recipeNumber = self.getRecipeNumber(record)
                record.setValue('number', recipeNumber)

                self.tblItems.model().addRecord(record)
                self.tblItems.model().reset()
                self.tblItems.setCurrentRow(self.tblItems.model().rowCount() - 1)
        except Exception as ex:
            QtGui.QMessageBox.question(self, u'Внимание', ex.message, QMessageBox.Close)

    def getEventInfo(self, context):
        date = QtCore.QDate.currentDate()
        client = context.getInstance(CClientInfo, self.clientId, date)
        if len(client.socStatuses) == 0:        # на случай нового обращения
            client.setSocStatuses(context.getInstance(CClientSocStatusInfoList, clientId=self.clientId))

        setPerson = context.getInstance(CPersonInfo, self.personId)

        return client, setPerson

    def getRecipeNumber(self, record):
        # TODO: mdldml: переписать этот метод, ужасно же
        counterCode = getBookkeeperCode(self.personId)
        if not counterCode:
            raise Exception(u'Не указан бухгалтерский код подразделения. Бухгалтерский код необходимо указывать у текущего подразделения или у одного из его головных подразделений. Текущим считается подразделение, которому принадлежит врач.')
        counterValue = None
        if counterCode: # FIXME: Why??
            counterValue = getDocumentNumber(self.clientId, counterCode, forceInt(record.value('finance_id')))
            if counterValue and QString(counterValue).contains('#'):
                seria = QString(counterValue).section('#', 0, 0)
                number = QString(counterValue).section('#', 1, 1)
                if QtGui.qApp.justifyDrugRecipeNumber():
                    number = number.rightJustified(7, QChar('0'))
                counterValue = seria + '#' + number

        if counterValue:
            return counterValue
        else:
            raise Exception(u'Не найден счётчик с кодом, совпадающим с кодом для бухгалтерии текущего либо головного подразделения')

    # @SimpleThread
    def sendRecipesThread(self):
        if QtGui.qApp.defaultKLADR().startswith('23'):
            recipesExchangeClientId = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'recipesExchangeClientId', ''))
            url = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'recipesExchangeUrl', ''))
            logDir = os.path.join(QtGui.qApp.logDir, 'recipesDebug.log')
            if forceBool(QtGui.qApp.preferences.appPrefs['recipesLog']):
                sender = CR23RecipeService(recipesExchangeClientId, url=url, tracefilename=logDir)
            else:
                sender = CR23RecipeService(recipesExchangeClientId, url=url)
            if not sender.checkClient(self.clientId):
                sender.sendClient(self.clientId)
            sender.sendRecipes([forceInt(item.value('id')) for item in self.modelItems.items() if not forceBool(item.value('sentToMiac')) and not forceInt(item.value('status'))])

    def sendRecipes(self):
        if forceBool(QtGui.qApp.preferences.appPrefs['recipesExchangeEnabled']):
            self.sendRecipesThread()
            # thread = self.sendRecipesThread()
            # thread.start()

    @QtCore.pyqtSlot()
    def on_actDrugstore_triggered(self):
        CEventRecipesDrugstore(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPrint_triggered(self):
        currentItem = self.tblItems.currentIndex()
        if not currentItem.isValid():
            return

        context = CInfoContext()
        drugRecipeInfo = context.getInstance(CDrugRecipeInfo, None, record=self.tblItems.model().items()[currentItem.row()])
        if not drugRecipeInfo.number or len(drugRecipeInfo.number) == 0:
            QtGui.QMessageBox.question(self, u'Внимание', u'Не был сформирован номер рецепта!')
            return

        if not drugRecipeInfo.finance.code in ['70', '71', '72', '73']:
            QtGui.QMessageBox.question(self, u'Внимание', u'Неверный код финансирования! Допустимы только коды 70, 71, 72 и 73.')
            return

        client, person = self.getEventInfo(context)

        policyStr = u''
        if len(client.policy.serial) > 0:
            policyStr = client.policy.serial + u' '
        policyStr += client.policy.number

        if drugRecipeInfo.printMnn and drugRecipeInfo.formularyItem.mnn.code != u'1':
            drugCode = drugRecipeInfo.formularyItem.mnn.code
            drugName = drugRecipeInfo.formularyItem.mnn.latinName
        else:
            drugCode = drugRecipeInfo.formularyItem.tradeName.code
            drugName = drugRecipeInfo.formularyItem.tradeName.latinName

        data = {
            'orgCode'           : forceString(getBookkeeperCode(self.personId)).rjust(5, '0'),
            'ogrn'              : person.organisation.OGRN.ljust(15, u' '),
            'socCode'           : drugRecipeInfo.socCode.ljust(3, u' '),
            'mkbCode'           : drugRecipeInfo.mkb.ljust(6, u' '),
            'characterId'       : self.characterId,
            'financeSel'        : {'70': 1, '71': 2, '72': 3, '73': 4}[drugRecipeInfo.finance.code],
            'percentSel'        : 1 if forceInt(drugRecipeInfo.percentage) == 50 else 0,
            'termSel'           : drugRecipeInfo.term,
            'recipeSeria'       : drugRecipeInfo.number.split('#')[0],
            'recipeNumber'      : drugRecipeInfo.number.split('#')[1],
            'recipeDate'        : drugRecipeInfo.dateTime.toString('dd.MM.yyyy'),
            'clientLastName'    : client.lastName,
            'clientFirstName'   : client.firstName,
            'clientPatrName'    : client.patrName,
            'clientSnils'       : unicode(client.SNILS),
            'clientBirthDate'   : client.birthDate.toString('dd.MM.yyyy'),
            'clientPolicyNumber': policyStr.ljust(25, u' '),
            'clientId'          : drugRecipeInfo.pregCard if drugRecipeInfo.pregCard > 0 else client.id,
            'clientRegAddress'  : client.regAddress,
            'doctor'            : person,
            'doctorName'        : person.longName,
            'doctorCode'        : unicode(person.federalCode)[:6].ljust(6, u' '),
            'mnn'               : drugName,
            'mnnCode'           : drugCode,
            'tradeName'         : drugRecipeInfo.formularyItem.tradeName,
            'issueForm'         : drugRecipeInfo.formularyItem.issueForm.name,
            'issueFormLat'      : drugRecipeInfo.formularyItem.issueForm.latinName,
            'dosage'            : drugRecipeInfo.dosage,
            'qnt'               : drugRecipeInfo.qnt,
            'signa'             : drugRecipeInfo.signa,
            'duration'          : drugRecipeInfo.duration,
            'numPerDay'         : drugRecipeInfo.numPerDay
        }

        templateId = getFirstPrintTemplate('recipe_new')[1]
        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_actEdit_triggered(self):
        row = self.tblItems.selectionModel().currentIndex().row()
        if 0 <= row < self.tblItems.model().rowCount() - 1:
            record = self.tblItems.model().items()[row]

            context = CInfoContext()
            client, setPerson = self.getEventInfo(context)

            dlg = CRecipeEditDialog(self, client.socStatuses, client.id, setPerson.personId)
            dlg.setRecord(record)
            if dlg.exec_() == QDialog.Accepted:
                dlg.getRecord(record)
                self.tblItems.model().reset()

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        row = self.tblItems.selectionModel().currentIndex().row()
        if row < self.tblItems.model().rowCount() - 1:
            item = self.tblItems.model().items()[row]
            if not forceBool(item.value('sentToMiac')):
                self.tblItems.model().removeRows(row, 1)
                self.tblItems.model().reset()

    @QtCore.pyqtSlot()
    def on_actAnnul_triggered(self):
        currentItem = self.tblItems.currentIndex()
        recipeRecord = self.tblItems.model().items()[currentItem.row()]
        dlg = CRecipeAnnulmentDialog(self, recipeRecord.value('id').isNull())
        if dlg.exec_() == QDialog.Accepted:
            recipeRecord.setValue('status', toVariant(dlg.getRecipeStatusCode()))
            self.tblItems.model().reset()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelItems_currentChanged(self, current, previous):
        row = self.tblItems.currentIndex().row()
        items = self.tblItems.model().items()
        self.actEdit.setEnabled(row >= 0 and row != len(items) and (items[row].value('id').isNull() or not forceBool(items[row].value('sentToMiac'))))
        self.actDelete.setEnabled(row >= 0 and row != len(items) and not forceBool(items[row].value('sentToMiac')))
        self.actPrint.setEnabled(row != len(items))

    def canClose(self):
        if len([item for item in self.tblItems.model().items() if item.value('id').isNull()]) > 0:
            if not self.eventId:
                QtGui.QMessageBox.information(self, u'Внимание!', u'Для отказа от создания обращения нужно удалить льготные рецепты!')
            else:
                QtGui.QMessageBox.information(self, u'Внимание!', u'Для отмены внесенных изменений нужно удалить льготные рецепты!')
            return False
        return True


class CEventRecipesPage(CFastEventRecipesPage):
    def __init__(self, parent=None):
        CFastEventRecipesPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()


class CValueCol(CIntCol):
    """
      Int column with units
    """

    def __init__(self, title, fields, defaultWidth, unitText, alignment='l'):
        CIntCol.__init__(self, title, fields, defaultWidth, alignment)
        self._unitText = unitText

    def format(self, values):
        return toVariant(forceString(values[0]) + ' ' + self._unitText)


class CRecNumCol(CInDocTableCol):
    """
        Recipe number column
    """

    def toString(self, val, record):
        val = forceString(val)
        if len(val) == 0:
            return u'(нет)'
        return val.replace(u'#', u' ')


class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'DrugRecipe', 'id', 'event_id', parent)
        self.addCol(CDateTimeInDocTableCol(u'Дата/время', 'dateTime', 20)).setReadOnly()
        self.addCol(CRecNumCol(u'Номер', 'number', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'Код', 'socCode', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'№ карты беременной', 'pregCard', 50)).setReadOnly()
        self.addCol(CRBInDocTableCol(u'Тип финансирования', 'finance_id', 50, 'rbFinance', showFields=CRBComboBox.showCodeAndName)).setReadOnly()
        self.addCol(CInDocTableCol(u'Процент оплаты', 'percentage', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'МКБ', 'mkb', 50)).setReadOnly()
        self.addCol(CRBInDocTableCol(u'Препарат', 'formularyItem_id', 50, 'DloDrugFormulary_Item', showFields=CRBComboBox.showCodeAndName)).setReadOnly()
        self.addCol(CInDocTableCol(u'Дозировка', 'dosage', 50)).setReadOnly()
        self.addCol(CInDocTableCol(u'Количество', 'qnt', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'Продолжительность (дней)', 'duration', 50)).setReadOnly()
        self.addCol(CInDocTableCol(u'Приёмов в день', 'numPerDay', 50)).setReadOnly()
        self.addCol(CInDocTableCol(u'Порядок приёма', 'signa', 50)).setReadOnly()
        self.addCol(CBoolInDocTableCol(u'Наличие протокола ВК', 'isVk', 15)).setReadOnly()
        self.addCol(CEnumInDocTableCol(u'Срок действия', 'term', 12, [u'5 дней', u'10 дней', u'1 месяц', u'3 месяца'])).setReadOnly()
        self.addCol(CEnumInDocTableCol(u'Статус', 'status', 20, recipeStatusNames)).setReadOnly()  # ], 'DrugRecipe').setReadOnly() #TODO: mdldml: подумать. как выразить в терминах CRecipeStatusModel
        self.addHiddenCol('sentToMiac')
        self.addHiddenCol('printMnn')
