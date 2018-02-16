# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
import os

from PyQt4 import QtGui, QtCore

from Exchange.R23.recipes.RecipeService import CR23RecipeService
from Exchange.R23.recipes.Ui_SynchronizeDLOMIAC import Ui_SynchronizeDLOMIACDialog
from library.DialogBase import CConstructHelperMixin
from library.TableModel import CTableModel, CDateTimeCol, CTextCol, CIntCol, CRefBookCol, CEnumCol, CBoolCol, \
    CDesignationCol
from library.Utils import forceString, toVariant, getVal, forceInt, forceRef, getPref, setPref, forceBool
from library.crbcombobox import CRBComboBox


class CSynchronizeDLOMIAC(QtGui.QDialog, CConstructHelperMixin, Ui_SynchronizeDLOMIACDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.addModels('DrugRecipe', CDrugRecipeModel(self))
        self.setModels(self.tblDrugRecipe, self.modelDrugRecipe, self.selectionModelDrugRecipe)
        self.tblDrugRecipe.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.connect(self.tblDrugRecipe.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.on_selectionModelDrugRecipe_selectionChanged)

        self.restorePreferences()

        self.setWindowTitle(u'Синхронизация с ПЦ ЛЛО МИАЦ')

    def restorePreferences(self):
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CSynchronizeDLOMIAC', {})
        # self.tblDrugRecipe.loadPreferences(preferences)
        width = forceInt(getPref(preferences, 'width', self.width()))
        height = forceInt(getPref(preferences, 'height', self.height()))
        self.resize(width, height)
        x = forceInt(getPref(preferences, 'x', self.pos().x()))
        y = forceInt(getPref(preferences, 'y', self.pos().y()))
        self.move(x, y)

    def reloadItems(self):
        db = QtGui.qApp.db
        tableDR = db.table('DrugRecipe')
        tableEvent = db.table('Event')
        table = tableDR.innerJoin(tableEvent, tableDR['event_id'].eq(tableEvent['id']))
        idList = db.getIdList(table, idCol=tableDR['id'], where=db.joinAnd([tableDR['sentToMiac'].eq(0),
                                                                            tableDR['dateTime'].dateGe(self.edtBegDate.date()),
                                                                            tableDR['dateTime'].dateLe(self.edtEndDate.date()),
                                                                            tableEvent['deleted'].eq(0),
                                                                            tableDR['deleted'].eq(0)]))
        self.tblDrugRecipe.model().setIdList(idList)
        self.btnSync.setEnabled(bool(idList))
        self.refreshStatus()

    def refreshStatus(self):
        countSelected = len(self.selectionModelDrugRecipe.selectedRows())
        countTotal = self.modelDrugRecipe.rowCount()
        self.lblStatus.setText(u'Записей в таблице выделено/всего: %s/%s' % (countSelected, countTotal))

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelDrugRecipe_selectionChanged(self, selected, deselected):
        self.refreshStatus()

    @QtCore.pyqtSlot()
    def on_btnLoad_clicked(self):
        self.reloadItems()

    @QtCore.pyqtSlot()
    def on_btnSync_clicked(self):
        db = QtGui.qApp.db
        recipesExchangeClientId = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'recipesExchangeClientId', ''))
        url = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'recipesExchangeUrl', ''))
        logDir = os.path.join(QtGui.qApp.logDir, 'recipesDebug.log')
        if forceBool(QtGui.qApp.preferences.appPrefs['recipesLog']):
            sender = CR23RecipeService(recipesExchangeClientId, url=url, tracefilename=logDir)
        else:
            sender = CR23RecipeService(recipesExchangeClientId, url=url)
        idList = []
        for index in self.tblDrugRecipe.selectionModel().selectedRows():
            idList.append(forceRef(self.modelDrugRecipe.getRecordByRow(index.row()).value('id')))
        if idList:
            chunkSize = 1
            chunks = [idList[index:(index + chunkSize)] for index in range(0, len(idList), chunkSize)]
            failures = False
            stmt = u'''
            SELECT
                Client.id
            FROM
                Client
                INNER JOIN Event ON Event.client_id = Client.id
                INNER JOIN DrugRecipe ON Event.id = DrugRecipe.event_id
            WHERE
                DrugRecipe.id IN (%s)
            '''
            for chunk in chunks:
                clientIdList = db.getIdList(table=None, stmt=stmt % ', '.join(map(str, chunk)))
                for clientId in clientIdList:
                    if not sender.checkClient(clientId):
                        sender.sendClient(clientId)
                newFailures = sender.sendRecipes(chunk)
                failures = failures or newFailures
            if failures:
                QtGui.QMessageBox.information(self, u'Внимание!', u'Передача завершена с ошибками.')
            else:
                QtGui.QMessageBox.information(self, u'', u'Передача завершена успешно.')
        self.reloadItems()

    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        self.tblDrugRecipe.selectAll()

    @QtCore.pyqtSlot()
    def on_btnDeselectAll_clicked(self):
        self.tblDrugRecipe.clearSelection()

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    def savePreferences(self):
        preferences = {}  # self.tblDrugRecipe.savePreferences()
        setPref(preferences, 'width', self.width())
        setPref(preferences, 'height', self.height())
        setPref(preferences, 'x', self.pos().x())
        setPref(preferences, 'y', self.pos().y())
        setPref(QtGui.qApp.preferences.windowPrefs, 'CSynchronizeDLOMIAC', preferences)

    def closeEvent(self, event):
        self.savePreferences()
        QtGui.QDialog.closeEvent(self, event)


class CValueCol(CIntCol):
    """
      Int column with units
    """
    def __init__(self, title, fields, defaultWidth, unitText, alignment='l'):
        CIntCol.__init__(self, title, fields, defaultWidth, alignment)
        self._unitText = unitText

    def format(self, values):
        return toVariant(forceString(values[0]) + ' ' + self._unitText)


class CRecNumCol(CTextCol):
    """
        Recipe number column
    """
    def format(self, values):
        val = forceString(values[0])
        if len(val) == 0:
            return u'(нет)'

        val = val.replace(u'#', u' ')
        return val

class CBookkeeperCodeCol(CDesignationCol):

    def format(self, values):
        # Возможно, это логичнее перенести в getValues, и вынести всю логику ВМ по получению bookkeeperCode в Orgs.Utils
        orgStructureId = forceRef(self.getValues(values)[0])
        code = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'bookkeeperCode'))
        while(not code):
            # Получить вышестоящее подразделение
            orgStructureId = forceInt(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
            if not orgStructureId:
                # Выше никого нет, текущий код - искомый
                break
            # Новый код
            code = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'bookkeeperCode'))
        return toVariant(code)

class CDrugRecipeModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CBookkeeperCodeCol(u'Код ОМС',        ['event_id'], [('Event', 'execPerson_id'),
                                                                 ('vrbPersonWithSpeciality', 'orgStructure_id')], 20),
            CTextCol(    u'Описание ошибки',      [ 'errorCode' ], 100),
            CDesignationCol(u'ФИО пациента',      [ 'event_id' ], [('Event', 'client_id'),
                                                                   ('Client', 'CONCAT_WS(" ", lastName, firstName, patrName)')], 35),
            CDesignationCol(u'Дата рождения',     [ 'event_id' ], [('Event', 'client_id'),
                                                                   ('Client', 'birthDate')],   20),
            CDateTimeCol(u'Дата/время',           [ 'dateTime' ],   20),
            CRecNumCol(  u'Серия и номер рецепта',[ 'number' ],     20),
            CTextCol(    u'Код льготы',           [ 'socCode' ], 20),
            CIntCol(     u'№ карты беременной',   [ 'pregCard' ], 50),
            CRefBookCol( u'Источник финансирования',[ 'finance_id' ], 'rbFinance', 50, CRBComboBox.showCodeAndName),
            CIntCol(     u'Процент оплаты',       [ 'percentage' ], 20),
            CTextCol(    u'МКБ',                  [ 'mkb' ], 50),
            CRefBookCol( u'Препарат',             [ 'formularyItem_id' ], 'DloDrugFormulary_Item', 50, CRBComboBox.showCodeAndName),
            CTextCol(    u'Дозировка',            [ 'dosage' ],      50),
            CIntCol(     u'Количество',           [ 'qnt' ],        20),
            CValueCol(   u'Продолжительность',    [ 'duration' ],   50, u'дней'),
            CIntCol(     u'Приёмов в день',       [ 'numPerDay'],     50),
            CTextCol(    u'Порядок приёма',       [ 'signa' ],      50),
            CBoolCol(    u'Наличие протокола ВК', [ 'isVk' ],       15),
            CEnumCol(    u'Срок действия',        [ 'term' ],   [ u'5 дней', u'10 дней', u'1 месяц', u'3 месяца' ], 12),
            CEnumCol(    u'Статус',               [ 'status' ], [u'Действителен', u'Недействителен', u'Испорчен'], 20),
            CDesignationCol(u'Врач',              [ 'event_id'], [('Event', 'execPerson_id'),
                                                                  ('vrbPersonWithSpeciality', 'name')], 35),
        ],
         'DrugRecipe')
