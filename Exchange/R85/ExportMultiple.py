# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   01.12.2015
'''

import os

from PyQt4 import QtCore, QtGui

from Accounting.Utils import getAccountExportFormat
from Exchange.R85.ExportR85TF import CExportR85TFEngine, CExportR85HTTFEngine
from Exchange.R85.ExportR85DDTF import CExportR85DDTFEngine
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer
from library.Utils import forceStringEx, forceTr, getPref, setPref, getClassName, CLogHandler

def exportR85Multiple(widget, accountIdList):
    exportWindow = CMultipleExportDialog(QtGui.qApp.db, accountIdList, widget)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), {})
    exportWindow.setParams(params)
    exportWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), exportWindow.params())

class CMultipleExportDialog(QtGui.QDialog):
    InitState = 0
    ExportState = 1
    SaveState = 2

    def __init__(self, db, accountIdList, parent=None):
        super(CMultipleExportDialog, self).__init__(parent=parent)
        self._db = db
        self._accountIdList = accountIdList
        self._engines = []
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        # self._engine = engine(db, accountRecord, progressInformer=self._pi)
        # self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()

    def setParams(self, params):
        if isinstance(params, dict):
            outDir = forceStringEx(getPref(params, 'outDir', u''))
            if os.path.isdir(outDir):
                self.edtSaveDir.setText(outDir)

    def params(self):
        params = {}
        setPref(params, 'outDir', forceStringEx(self.edtSaveDir.text()))
        return params

    @property
    def currentState(self):
        return self._currentState

    @currentState.setter
    def currentState(self, value):
        if value in [self.InitState, self.ExportState, self.SaveState]:
            self._currentState = value
            self.onStateChanged()

    def onStateChanged(self):
        self.btnNextAction.setText(self._actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ExportState)
        # self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbExport.setEnabled(self.currentState == self.ExportState)
        self.gbSave.setEnabled(self.currentState == self.SaveState)
        self.btnSave.setEnabled(self.hasDocuments())
        QtCore.QCoreApplication.processEvents()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        # self.gbInit = QtGui.QGroupBox()
        # gbLayout = QtGui.QVBoxLayout()
        # self.gbInit.setLayout(gbLayout)
        # layout.addWidget(self.gbInit)

        # export block
        self.gbExport = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self._pi.progressChanged.connect(self.progressBar.setProgress)
        gbLayout.addWidget(self.progressBar)
        self.gbExport.setLayout(gbLayout)
        layout.addWidget(self.gbExport)

        # save block
        self.gbSave = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtSaveDir = QtGui.QLineEdit(QtCore.QDir.homePath())
        self.edtSaveDir.setReadOnly(True)
        lineLayout.addWidget(self.edtSaveDir)
        self.btnBrowseDir = QtGui.QToolButton()
        self.btnBrowseDir.clicked.connect(self.onBrowseDir)
        lineLayout.addWidget(self.btnBrowseDir)
        gbLayout.addLayout(lineLayout)
        lineLayout = QtGui.QHBoxLayout()
        self.btnSave = QtGui.QPushButton()
        self.btnSave.clicked.connect(self.onSaveClicked)
        lineLayout.addWidget(self.btnSave)
        gbLayout.addLayout(lineLayout)
        self.gbSave.setLayout(gbLayout)
        layout.addWidget(self.gbSave)

        # log block
        self.logInfo = QtGui.QTextEdit()
        layout.addWidget(self.logInfo)
        # self._loggerHandler.logged.connect(self.logInfo.append)

        # buttons block
        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()

        self.setModal(True)

    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Экспорт. Крым. ФЛК', context))
        # self.gbInit.setTitle(forceTr(u'Параметры экспорта', context))

        self.gbExport.setTitle(forceTr(u'Экспорт', context))

        self.gbSave.setTitle(forceTr(u'Сохранение результата', context))
        self.btnSave.setText(forceTr(u'Сохранить', context))

        self._actionNames = {self.InitState: forceTr(u'Экспорт', context),
                             self.ExportState: forceTr(u'Прервать', context),
                             self.SaveState: forceTr(u'Повторить', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))

    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            result = False
            self.currentState = self.ExportState
            for accountId in self._accountIdList:
                engine = None
                exportInfo = getAccountExportFormat(accountId).split()
                if exportInfo:
                    exportFormat = exportInfo[0]
                    if exportFormat in ('R85XML'):
                        engine = CExportR85TFEngine(self._db, progressInformer=self._pi, FLC=True)
                    # Крым, выгрузка диспансеризации и профосмотров (МО->Фонд)
                    elif exportFormat == 'R85DDXML':
                        engine = CExportR85DDTFEngine(self._db, progressInformer=self._pi, FLC=True)
                    elif exportFormat == 'R85HTXML':
                        engine = CExportR85HTTFEngine(self._db, progressInformer=self._pi, FLC=True)
                    if engine:
                        # FIXME: может провоцировать падения/ошибки?
                        CLogHandler(engine.logger(), self).logged.connect(self.logInfo.append)
                        self._engines.append(engine)
                        try:
                            result = engine.process(accountId)
                        except:
                            self.currentState = self.InitState
                            raise
            self.currentState = self.SaveState if result else self.InitState
        elif self.currentState == self.ExportState:
            for engine in self._engines:
                engine.terminate()
            self._engines = []
        elif self.currentState == self.SaveState:
            self.currentState = self.InitState
        self.onStateChanged()

    def canClose(self):
        ok = self.currentState == self.SaveState
        return ok or \
               QtGui.QMessageBox.warning(self,
                                         u'Внимание!',
                                         u'Остались несохраненные файлы выгрузок,\n'
                                         u'которые будут утеряны.\n'
                                         u'Вы уверены, что хотите покинуть менеджер экспорта?\n',
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                         QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes

    def hasDocuments(self):
        result = False
        for engine in self._engines:
            if engine.hDocuments or engine.lDocuments:
                result = True
                break
        return result
    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()

    def done(self, result):
        if self.canClose():
            super(CMultipleExportDialog, self).done(result)

    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def onBrowseDir(self):
        saveDir = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self,
                                                         u'Укажите директорию для сохранения файлов выгрузки',
                                                         self.edtSaveDir.text()))
        if os.path.isdir(saveDir):
            self.edtSaveDir.setText(saveDir)

    @QtCore.pyqtSlot()
    def onSaveClicked(self):
        self.btnClose.setEnabled(False)
        for engine in self._engines:
            engine.save(self.edtSaveDir.text())
        self.onStateChanged()
