# -*- coding: utf-8 -*-
import os

from PyQt4 import QtGui, QtCore

from Events.Ui_EventRecipesDrugstore import Ui_EventRecipesDrugstore
from Exchange.R23.recipes.RecipeService import CR23RecipeService
from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CTextCol, CIntCol, CCol, CDecimalCol
from library.Utils import toVariant, forceDouble, forceStringEx, forceString, getVal, forceInt, forceBool


class CEventRecipesDrugstore(CDialogBase, Ui_EventRecipesDrugstore):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Drugstore', CEventRecipesDrugstoreModel(self))
        self.setModels(self.tblItems, self.modelDrugstore, self.selectionModelDrugstore)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setWindowTitle(u'Наличие ЛС в аптеках')
        self.search('')
        self.syncLabel()

    @QtCore.pyqtSlot()
    def on_btnSearch_clicked(self):
        self.startSearch()

    def startSearch(self):
        self.search(forceStringEx(self.edtName.text()))

    def search(self, like=''):
        db = QtGui.qApp.db
        table = db.table('dlo_DrugstoreRemains')
        cond = [table['deleted'].eq(0), table['quantity'].gt(0)]
        condlike = []
        if like != '':
            condlike = [table['productName'].like('%' + like + '%'),
                        table['mnn'].like('%' + like + '%'),
                        table['trn'].like('%' + like + '%')]
        where = db.joinAnd([db.joinAnd(cond), db.joinOr(condlike)]) if condlike else db.joinAnd(cond)
        idList = db.getIdList(table, idCol=table['id'], where=where)
        self.tblItems.model().setIdList(idList)

    def syncLabel(self):
        db = QtGui.qApp.db
        table = db.table('dlo_DrugstoreRemains')
        record = db.getRecordEx(table, '*', table['deleted'].eq(0))
        if record:
            if (record.value('syncDateTime')):
                lastSync = forceString(record.value('syncDateTime'))
                self.lblLastSync.setText(u'Дата и время последней синхронизации: %s' % lastSync)
        else:
            self.lblLastSync.setText(u'Синхронизации не производились')

    @QtCore.pyqtSlot()
    def on_btnSync_clicked(self):
        res = QtGui.QMessageBox.warning( self,
                                         u'Внимание!',
                                         u'Данная операция может выполняться долго. Продолжить?',
                                         QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
                                         QtGui.QMessageBox.Cancel)
        if res == QtGui.QMessageBox.Ok:
            recipesExchangeClientId = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'recipesExchangeClientId', ''))
            url = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'recipesExchangeUrl', ''))
            logDir = os.path.join(QtGui.qApp.logDir, 'recipesDebug.log')
            if forceBool(QtGui.qApp.preferences.appPrefs['recipesLog']):
                sender = CR23RecipeService(recipesExchangeClientId, url=url, tracefilename=logDir)
            else:
                sender = CR23RecipeService(recipesExchangeClientId, url=url)
            QtGui.qApp.callWithWaitCursor(self, sender.downloadRemains)
            self.syncLabel()

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.startSearch()
        CDialogBase.keyPressEvent(self, event)


class CEventRecipesDrugstoreModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(u'Препарат', ['productName'], 60),
            CTextCol(u'МНН', ['mnn'], 30),
            CTextCol(u'Аптека', ['drugstoreName'], 40),
            CDecimalCol(u'Количество', ['quantity'], 10),
            CPriceCol(u'Цена', ['price'], 10)
        ], 'dlo_DrugstoreRemains')


class CPriceCol(CCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)

    def format(self, values):
        return toVariant(forceDouble(values[0]))

    def formatNative(self, values):
        return forceDouble(values[0])