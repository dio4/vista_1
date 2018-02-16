# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import codecs
import os
import time

from PyQt4 import QtCore, QtGui, QtSql

from library.LoggingModule import Logger
from library.database       import CTable, CField
from library.DialogBase     import CDialogBase
from library.exception      import CException
from library.PrintInfo      import CInfoContext
from library.Utils          import forceBool, forceInt, forceRef, forceString, forceStringEx, toVariant

from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog

from Registry.Utils         import CClientInfo

from Ui_LogicalControlDoubles import Ui_LogicalControlDoubles


## Табличная модель на основании словаря словарей.
# Каждый элемент основного словаря (подсловарь) - это строка таблицы..
# столбцы заполняются на основании значений в подсловаре с учетом настроенной связи между номером столбца и ключем подсловаря (_mapColumnToKey)
class CDictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent = None):
        super(CDictTableModel, self).__init__(parent)
        self._mapColumnToKey = []
        self._sourceDict = {} # Исходный словарь словарей
        self._sourceKeyList = [] #Упорядоченный список ключей исходного словаря (для сопостовления номера строки элементу исходного словаря).
        self.resetHighlight()
    
    def clearColumnInfo(self):
        self._mapColumnToKey = []
        self.reset()
        
    
    def addCollumnInfo(self, keyName, columnName):
        self._mapColumnToKey.append((keyName, columnName))
    
    
    def setSourceDict(self, sourceDict, sortKey = None):
        self._sourceDict = sourceDict
        self._sourceKeyList = sourceDict.keys()
        if sortKey:
            self._sourceKeyList.sort(key = lambda sourceKey: self._sourceDict[sourceKey].get(sortKey, None))
        self.reset()
        
    
    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self._sourceKeyList)
    
    
    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self._mapColumnToKey)
    
    
    def getRowDict(self, row):
        if row not in xrange(self.rowCount()):
            return {}
        rowKey = self._sourceKeyList[row]
        return self._sourceDict.get(rowKey, {})
    
    
    def updateRowKey(self, row, newKey):
        rowDict = self._sourceDict.pop(self._sourceKeyList[row])
        self._sourceKeyList[row] = newKey
        self._sourceDict[newKey] = rowDict
        
    
    
    def getRowKey(self, row):
        if row not in xrange(self.rowCount()):
            return {}
        return self._sourceKeyList[row]
    
    
    def removeKey(self, key):
        self._sourceDict.pop(key)
        self._sourceKeyList.remove(key)
        self.reset()
    
    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and section in xrange(self.columnCount()) and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._mapColumnToKey[section][1])
        
        return QtCore.QVariant()

    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        
        row = index.row()
        if row not in xrange(self.rowCount()):
            return QtCore.QVariant()
        
        column = index.column()
        if column not in xrange(self.columnCount()):
            return QtCore.QVariant()
        
        if role == QtCore.Qt.DisplayRole:
            rowDict = self.getRowDict(row)
            if not rowDict:
                return QtCore.QVariant()
            
            columnKey = self._mapColumnToKey[column][0]
            columnValue = rowDict.get(columnKey, None) 
            
            return QtCore.QVariant(columnValue)
        elif self._highlightCompare and role == QtCore.Qt.BackgroundColorRole:
            rowDict = self.getRowDict(row)
            if not rowDict:
                return QtCore.QVariant()
            
            if rowDict.get(self._highlightCompare[0], None) == self._highlightCompare[1]:
                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(100, 255, 100)))
    
        return QtCore.QVariant()
    
    
    def setHighlightRows(self, compareKey, compareValue):
        self._highlightCompare = (compareKey, compareValue)
        
    
    def resetHighlight(self):
        self._highlightCompare = None


class CControlDoubles(CDialogBase, Ui_LogicalControlDoubles):
    
#     dateFormat = 'dd.MM.yyyy'
    templateExt = '.tmpl'
        
    def __init__(self, parent, isFromRegistry=False, condFromRegistry=None):
        super(CControlDoubles, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.prbControlDoubles.setFormat('%p%')
        self.prbControlDoubles.setValue(0)
        self.checkRun = False
        self.booleanNewTuning = True
        self.findLikeStings = None
        
        self.rows = 0
        self.errorStr = u''
        
        self.spbBirthPlaceComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        self.spbDocumentComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        self.spbLocAddressComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        self.spbNameComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        self.spbPolicyComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        self.spbRegAddressComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        self.spbSNILSComparisonPrecision.valueChanged.connect(self.enableBtnSaveTemplate)
        
        self._checkBoxList = [self.chkBirthDate,
                              self.chkBirthPlace,
                              self.chkCreateDate,
                              self.chkCitizenship,
                              self.chkDocuments,
                              self.chkLocAddress,
                              self.chkName,
                              self.chkPolicy,
                              self.chkRegAddress,
                              self.chkSex,
                              self.chkSNILS]

        self._filters = [(self.chkName, self.spbNameComparisonPrecision),
                         (self.chkSex,  None),
                         (self.chkBirthDate, None),
                         (self.chkBirthPlace, self.spbBirthPlaceComparisonPrecision),
                         (self.chkCitizenship, None),
                         (self.chkDocuments, self.spbDocumentComparisonPrecision),
                         (self.chkLocAddress, self.spbLocAddressComparisonPrecision),
                         (self.chkRegAddress, self.spbRegAddressComparisonPrecision),
                         (self.chkCreateDate, None),
                         (self.chkSNILS, self.spbSNILSComparisonPrecision),
                         (self.chkPolicy, self.spbPolicyComparisonPrecision)]
        self._usedFilters = []

        if not isFromRegistry:
            for checkBoxWidget in self._checkBoxList:
                checkBoxWidget.toggled.connect(self.checkBoxStateChanged)
#        self.chkBirthDate.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkBirthPlace.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkCreateDate.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkCitizenship.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkDocuments.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkLocAddress.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkName.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkPolicy.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkRegAddress.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkSex.toggled.connect(self.enableBtnSaveTemplate)
#        self.chkSNILS.toggled.connect(self.enableBtnSaveTemplate)
        
        db= QtGui.qApp.db
        self.tableClient = db.table('Client')
        self.tableDuplicateClient = db.table('Client').alias('DuplicateClient')
        
        self.tableClientDocument = db.table('ClientDocument')
        self.tableDuplicateClientDocument = db.table('ClientDocument').alias('DuplicateClientDocument')
        self.tableClientPolicy = db.table('ClientPolicy')
        self.tableDuplicateClientPolicy = db.table('ClientPolicy').alias('DuplicateClientPolicy')
        self.tableClientSocStatus = db.table('ClientSocStatus')
        self.tableDuplicateClientSocStatus = db.table('ClientSocStatus').alias('DuplicateClientSocStatus')
        self.tableClientLocAddress = db.table('ClientAddress').alias('ClientLocAddress')
        self.tableDuplicateClientLocAddress = db.table('ClientAddress').alias('DuplicateClientLocAddress')
        self.tableClientRegAddress = db.table('ClientAddress').alias('ClientRegAddress')
        self.tableDuplicateClientRegAddress = db.table('ClientAddress').alias('DuplicateClientRegAddress')
        self.tableClientSocStatusType = db.table('rbSocStatusType')
        self.tableRBSocStatusClass = db.table('rbSocStatusClass')
        
        self.initFieldsInfo()
        
        self.clientsInfo = {}
        
        self.baseClientModel = CDictTableModel(self)
        self.baseClientModel.addCollumnInfo(self.getAlias('code', False), 
                                            self._fieldsInfo['code'].get('header', ''))
        self.baseClientModel.addCollumnInfo(self.getAlias('name', False), 
                                            self._fieldsInfo['name'].get('header', ''))
        self.tblBaseClient.setModel(self.baseClientModel)
        
        self.duplicateModel = CDictTableModel(self)
        self.tblDuplicateClient.setModel(self.duplicateModel)
        
        self.actChangeBaseClient = QtGui.QAction(u'Сделать базовым', self, triggered = self.changeBaseClient)
        self.actMergeAllToBase = QtGui.QAction(u'Объединить всех в базового', self, triggered = self.mergeAllToBase)
        self.tblDuplicateClient.createPopupMenu([self.actChangeBaseClient, self.actMergeAllToBase])
        
        self._abort = False
        self._isRun = False
        
        self.completedIdList = []
        self.uncompletedIdList = []
        
        self.showedColumns = []
        
        self._elapsedTimer = None
        self._clientId = None
        self.commonLogFileName = None

        self.isFromRegistry = isFromRegistry
        # Вызывается из рег.карты при обнаружении двойника и желании пользователя объединить его с базовым
        if isFromRegistry:
            self.tabWidget.setVisible(False)
            self.gbSearchTemplates.setVisible(False)
            for chk in self._checkBoxList:
                chk.setChecked(False)
            if condFromRegistry[0] == 'name':
                self.chkName.setChecked(True)
                self.chkBirthDate.setChecked(True)
            elif condFromRegistry[0] == 'doc':
                self.chkDocuments.setChecked(True)
            elif condFromRegistry[0] == 'snils':
                self.chkSNILS.setChecked(True)
            elif condFromRegistry[0] == 'policy':
                self.chkPolicy.setChecked(True)
            self.condFromRegistry = condFromRegistry[1]
            self.btnBeginCheck.setVisible(False)
            self.startSearch(False)
    
    def setClientId(self, clientId):
        self._clientId = clientId
        if clientId:
            clientInfo = CClientInfo(CInfoContext(), clientId)
            self.setWindowTitle(u'%s для пациента %s %s' % (self.windowTitle(),
                                                            clientId,
                                                            clientInfo.fullName))
        
    def clientId(self):
        return self._clientId
        
    
    def initFieldsInfo(self):
        self._fieldsInfo = {'code' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'id',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'Код',
                                      'sortIndex' : 0},
                            'lastName' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'lastName',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'',
                                      'sortIndex' : 1},
                            'firstName' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'firstName',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'',
                                      'sortIndex' : 2},
                            'patrName' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'patrName',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'',
                                      'sortIndex' : 3},
                            'name' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : ['lastName', 'firstName', 'patrName'],
                                      'alias' : 'name',
                                      'conversionFunc' : 'CONCAT_WS(\' \', %(lastName)s, %(firstName)s, %(patrName)s)',
                                      'header' : u'Ф.И.О.',
                                      'sortIndex' : 4},
                            'sex' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'sex',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'Пол',
                                      'sortIndex' : 5},
                            'SNILS' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'SNILS',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'СНИЛС',
                                      'sortIndex' : 6},
                            'createDatetime' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'createDatetime',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'Дата регистрации',
                                      'sortIndex' : 7},
                            'birthDate' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'birthDate',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'Дата рожд.',
                                      'sortIndex' : 8},
                            'birthPlace' : {'table' : self.tableClient,
                                      'dupTable' : self.tableDuplicateClient,
                                      'sourceFieldName' : 'birthPlace',
                                      'alias' : None,
                                      'conversionFunc' : None,
                                      'header' : u'Место рождения',
                                      'sortIndex' : 9},
                            'citizenship' : {'table' : self.tableClientSocStatusType,
                                      'dupTable' : self.tableClientSocStatusType,
                                      'sourceFieldName' : 'name',
                                      'alias' : 'citizenship',
                                      'conversionFunc' : None,
                                      'header' : u'Гражд.',
                                      'sortIndex' : 10},
                            'locAddress' : {'table' : self.tableClientLocAddress,
                                      'dupTable' : self.tableDuplicateClientLocAddress,
                                      'sourceFieldName' : 'id',
                                      'alias' : 'locAddress',
                                      'conversionFunc' : 'formatClientAddress(%(id)s)',
                                      'header' : u'Место проживания',
                                      'sortIndex' : 11},
                            'regAddress' : {'table' : self.tableClientRegAddress,
                                      'dupTable' : self.tableDuplicateClientRegAddress,
                                      'sourceFieldName' : 'id',
                                      'alias' : 'regAddress',
                                      'conversionFunc' : 'formatClientAddress(%(id)s)',
                                      'header' : u'Место регистрации',
                                      'sortIndex' : 12},
                            'docSerial' : {'table' : self.tableClientDocument,
                                      'dupTable' : self.tableDuplicateClientDocument,
                                      'sourceFieldName' : 'serial',
                                      'alias' : 'docSerial',
                                      'conversionFunc' : None,
                                      'header' : u'Серия док-та',
                                      'sortIndex' : 13},
                            'docNumber' : {'table' : self.tableClientDocument,
                                      'dupTable' : self.tableDuplicateClientDocument,
                                      'sourceFieldName' : 'number',
                                      'alias' : 'docNumber',
                                      'conversionFunc' : None,
                                      'header' : u'Номер док-та',
                                      'sortIndex' : 14},
                            'document' : {'table' : self.tableClientDocument,
                                      'dupTable' : self.tableDuplicateClientDocument,
                                      'sourceFieldName' : ['serial', 'number'],
                                      'alias' : 'document',
                                      'conversionFunc' : 'CONCAT_WS(\' \', %(serial)s, %(number)s)',
                                      'header' : u'Док-т',
                                      'sortIndex' : 15},
                            'policySerial' : {'table' : self.tableClientPolicy,
                                      'dupTable' : self.tableDuplicateClientPolicy,
                                      'sourceFieldName' : 'serial',
                                      'alias' : 'policySerial',
                                      'conversionFunc' : None,
                                      'header' : u'Серия полиса',
                                      'sortIndex' : 16},
                            'policyNumber' : {'table' : self.tableClientPolicy,
                                      'dupTable' : self.tableDuplicateClientPolicy,
                                      'sourceFieldName' : 'number',
                                      'alias' : 'policyNumber',
                                      'conversionFunc' : None,
                                      'header' : u'Номер полиса',
                                      'sortIndex' : 17},
                            'policy' : {'table' : self.tableClientPolicy,
                                      'dupTable' : self.tableDuplicateClientPolicy,
                                      'sourceFieldName' : ['serial', 'number'],
                                      'alias' : 'policy',
                                      'conversionFunc' : 'CONCAT_WS(\' \', %(serial)s, %(number)s)',
                                      'header' : u'Полис',
                                      'sortIndex' : 18}}
        # end of initFieldsInfo
        
    
    def getTableOfField(self, name, isBase = True):
        fieldInfo = self._fieldsInfo.get(name, {})
        table = fieldInfo.get('table' if isBase else 'dupTable', None)
        if not (table and isinstance(table, CTable)):
            raise CException(str(table))
        return table
    
    
    def getField(self, name, isBase = True):
        fieldInfo = self._fieldsInfo.get(name, {})
        table = self.getTableOfField(name, isBase)
        sourceFieldName = fieldInfo.get('sourceFieldName', '')
        if not isinstance(sourceFieldName, list):
            sourceFieldName = [sourceFieldName]
            
        conversionFunc = fieldInfo.get('conversionFunc', None)
        if conversionFunc and isinstance(conversionFunc, basestring):
            field = CField(QtGui.qApp.db, 
                           '', 
                           conversionFunc % dict([(fieldName, table[fieldName]) for fieldName in sourceFieldName]),
                           QtCore.QVariant.String)
        else:
            field = table[sourceFieldName[0]]
        return field
    
    
    def getAlias(self, name, isBase = True):
        fieldInfo = self._fieldsInfo.get(name, {})
        alias = fieldInfo.get('alias', None)
        prefix = 'base_' if isBase else ''
        sourceFieldName = fieldInfo.get('sourceFieldName', '')
        if not alias:
            alias = sourceFieldName[0] if isinstance(sourceFieldName, list) else sourceFieldName
        return prefix + alias
                         
    
    def getFieldDescription(self, name, isBase = True):       
        return self.getField(name, isBase).alias(self.getAlias(name, isBase))
        
          
    def setTemplateDir(self, templateDir):
        if not os.path.isdir(templateDir):
            templateDir = forceString(QtCore.QDir.homePath())
        
        self.edtTemplateDir.setText(templateDir)
        self.updateTemplateFileList()
    
    
    def templateDir(self):
        return forceString(self.edtTemplateDir.text())
    
    
    def loadSearchTemplate(self, fileName = None):
        settings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
        self.chkName.setChecked(forceBool(settings.value('byName', toVariant(True))))
        self.spbNameComparisonPrecision.setValue(forceInt(settings.value('namePrecision', toVariant(0))))
        
        self.chkSex.setChecked(forceBool(settings.value('bySex', toVariant(True))))
        
        self.chkBirthDate.setChecked(forceBool(settings.value('byBirthDate', toVariant(True))))
        
        self.chkBirthPlace.setChecked(forceBool(settings.value('byBirthPlace', toVariant(False))))
        self.spbBirthPlaceComparisonPrecision.setValue(forceInt(settings.value('BirthPlacePrecision', toVariant(0))))
        
        self.chkCitizenship.setChecked(forceBool(settings.value('byCitizenship', toVariant(False))))
        
        self.chkDocuments.setChecked(forceBool(settings.value('byDocuments', toVariant(False))))
        self.spbDocumentComparisonPrecision.setValue(forceInt(settings.value('documentPrecision', toVariant(0))))
        
        self.chkLocAddress.setChecked(forceBool(settings.value('byLocAddress', toVariant(False))))
        self.spbLocAddressComparisonPrecision.setValue(forceInt(settings.value('locAddressPrecision', toVariant(0))))
        
        self.chkRegAddress.setChecked(forceBool(settings.value('byRegAddress', toVariant(False))))
        self.spbRegAddressComparisonPrecision.setValue(forceInt(settings.value('regAddressPrecision', toVariant(0))))
        
        self.chkCreateDate.setChecked(forceBool(settings.value('byCreateDate', toVariant(False))))
        
        self.chkSNILS.setChecked(forceBool(settings.value('bySNILS', toVariant(False))))
        self.spbSNILSComparisonPrecision.setValue(forceInt(settings.value('SNILSPrecision', toVariant(0))))
        
        self.chkPolicy.setChecked(forceBool(settings.value('byPolicy', toVariant(False))))
        self.spbPolicyComparisonPrecision.setValue(forceInt(settings.value('policyPrecision', toVariant(0))))
        
        self.btnSaveTemplate.setEnabled(False)
        
    
    def saveSearchTemplate(self, fileName):
        if not fileName:
            return False
        
        settings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
        
        if settings.status() != QtCore.QSettings.NoError:
            return False
        
        settings.setValue('byName', toVariant(self.chkName.isChecked()))
        settings.setValue('namePrecision', toVariant(self.spbNameComparisonPrecision.value()))
        
        settings.setValue('bySex', toVariant(self.chkSex.isChecked()))
        
        settings.setValue('byBirthDate', toVariant(self.chkBirthDate.isChecked()))
        
        settings.setValue('byBirthPlace', toVariant(self.chkBirthPlace.isChecked()))
        settings.setValue('BirthPlacePrecision', toVariant(self.spbBirthPlaceComparisonPrecision.value()))
        
        settings.setValue('byCitizenship', toVariant(self.chkCitizenship.isChecked()))
        
        settings.setValue('byDocuments', toVariant(self.chkDocuments.isChecked()))
        settings.setValue('documentPrecision', toVariant(self.spbDocumentComparisonPrecision.value()))
        
        settings.setValue('byLocAddress', toVariant(self.chkLocAddress.isChecked()))
        settings.setValue('locAddressPrecision', toVariant(self.spbLocAddressComparisonPrecision.value()))
        
        settings.setValue('byRegAddress', toVariant(self.chkRegAddress.isChecked()))
        settings.setValue('regAddressPrecision', toVariant(self.spbRegAddressComparisonPrecision.value()))
        
        settings.setValue('byCreateDate', toVariant(self.chkCreateDate.isChecked()))
        
        settings.setValue('bySNILS', toVariant(self.chkSNILS.isChecked()))
        settings.setValue('SNILSPrecision', toVariant(self.spbSNILSComparisonPrecision.value()))
        
        settings.setValue('byPolicy', toVariant(self.chkPolicy.isChecked()))
        settings.setValue('policyPrecision', toVariant(self.spbPolicyComparisonPrecision.value()))
        settings.sync()
        
        return True
        
    
    def updateTemplateFileList(self):
        self.cmbTemplateName.clear()
        self.cmbTemplateName.addItem(u'<Не задано>')

        try:
            fileNameList = os.listdir(self.templateDir())
        except OSError, e:
            QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Не удалось загрузить список шаблонов поиска',
                                       QtGui.QMessageBox.Ok,
                                       QtGui.QMessageBox.Ok)
            return

        for fileName in fileNameList:
            if os.path.splitext(fileName)[1] != self.templateExt:
                continue
            self.cmbTemplateName.addItem(fileName)
            
        self.cmbTemplateName.setCurrentIndex(0)
        self.btnSaveTemplate.setEnabled(False)
    
    
    @QtCore.pyqtSlot(int)
    def on_cmbTemplateName_currentIndexChanged(self, idx):
        templateName = forceStringEx(self.cmbTemplateName.currentText())
        fileName = os.path.join(self.templateDir(), templateName)
        
        if not os.path.isfile(fileName):
            fileName = ''
        
        self.loadSearchTemplate(fileName)       
    
    
        
    @QtCore.pyqtSlot()
    def on_btnTemplateDirBrowse_clicked(self):
        templateDir = QtGui.QFileDialog.getExistingDirectory(self, u'Выберите директорию с шаблонами поиска')
        self.setTemplateDir(templateDir)
    
    
    @QtCore.pyqtSlot()
    def on_btnSaveTemplate_clicked(self):
        errorMessage = ''
        if '<' in self.cmbTemplateName.currentText():
            errorMessage = u'Необходимо задать имя для шаблона'
        else:
            templateName = forceStringEx(self.cmbTemplateName.currentText())
            if os.path.splitext(templateName)[1] != self.templateExt:
                templateName += self.templateExt
            fileName = os.path.join(self.templateDir(), templateName)
            if not self.saveSearchTemplate(fileName):
                errorMessage = u'Не удалось сохранить шаблон в файл\nПроверьте имя шаблона на корректность'
            else:
                templateIdx = self.cmbTemplateName.findText(templateName)
                if templateIdx == -1:
                    self.cmbTemplateName.addItem(templateName)
                    templateIdx = self.cmbTemplateName.count() - 1
                self.cmbTemplateName.setCurrentIndex(templateIdx)
                self.btnSaveTemplate.setEnabled(False)
        if errorMessage:
            QtGui.QMessageBox.warning(self, 
                                      u'Ошибка сохранения', 
                                      errorMessage, 
                                      buttons = QtGui.QMessageBox.Ok)
    
    
    
    @QtCore.pyqtSlot()
    def checkBoxStateChanged(self):
#        checkStateList = 
        if not reduce(lambda x, y: x or y,
                      [checkBoxWidget.isChecked() for checkBoxWidget in self._checkBoxList]):
            self.chkDocuments.setChecked(True)
        self.enableBtnSaveTemplate()
            
    
    
    @QtCore.pyqtSlot()
    def enableBtnSaveTemplate(self):
        self.btnSaveTemplate.setEnabled(True)
        
   

    @QtCore.pyqtSlot()
    def on_btnEndCheck_clicked(self):
        self.close()
        QtGui.qApp.emitCurrentClientInfoChanged()
        
            
    def closeEvent(self, event):
        if self._isRun:
            event.ignore()
        else:
            QtGui.QDialog.closeEvent(self, event)
    
    
    
    @QtCore.pyqtSlot()
    def on_btnContinue_clicked(self):
        if self._isRun:
            self._abort = True
        else:
            self.startSearch(True)


    @QtCore.pyqtSlot()
    def on_btnBeginCheck_clicked(self):
        self._usedFilters = [i for i, f in enumerate(self._filters) if f[0].isChecked()]
        self.startSearch(False)
        
    
    def startSearch(self, isContinue):
        self._abort = False
        self.commonLogFileName = os.path.join(self.templateDir(), u'duplicateCommonMergeLog_%s.log' % forceString(QtCore.QDateTime.currentDateTime().toString('ddMMyyyy_hh-mm-ss')))
        self.btnBeginCheck.setEnabled(False)
        self.btnEndCheck.setEnabled(False)
        self.btnContinue.setText(u'Прервать')
        self.actChangeBaseClient.setEnabled(False)
        self.actMergeAllToBase.setEnabled(False)
        self.gbSearchTemplates.setEnabled(False)
        self.tabWidget.setEnabled(False)
        self.btnContinue.setEnabled(True)
        self.btnPrint.setEnabled(False)



        self._elapsedTimer = time.time()
        if not isContinue:
            self.completedIdList = []
            self.uncompletedIdList = []
        try:
            self._isRun = True
            self.findDuplicates()
        finally:
            self.btnContinue.setEnabled(self._abort and bool(self.uncompletedIdList))
            self._isRun = False
            self.btnBeginCheck.setEnabled(True)
            self.btnEndCheck.setEnabled(True)
            self.btnContinue.setText(u'Продолжить')
            self.gbSearchTemplates.setEnabled(True)
            self.tabWidget.setEnabled(True)
            self.updateModels()
            self.lblElapsedTime.setText(forceString((time.time() - self._elapsedTimer)if self._elapsedTimer else 0))
            self._elapsedTimer = None
            


    def findDuplicates(self, inputCond=None):
        db = QtGui.qApp.db
        
        del self.clientsInfo
        self.clientsInfo= {}
        
        cols = [# Данные по базовому пациенту
                self.getFieldDescription('code', True),
                self.getFieldDescription('name', True),
                # Данные по дубликату
                self.getFieldDescription('code', False),
                self.getFieldDescription('name', False),
                ]
        
        self.showedColumns = ['code',
                              'name']
        
        queryTable = self.tableClient
        queryCond = ['1']

        if self.isFromRegistry and self.condFromRegistry:
            queryCond += self.condFromRegistry

        # -- НАЧАЛО -- Определение условий соединения таблицы Client с самой собой
        # Дабы минимизировать итоговую (после джойнов) таблицу, все возможные урезающие условия помещаются в условия для inner join'ов
        # При этом сначала к основной таблице Client присоединяются связанные с ней доп. таблицы с данными основного пациента (адресами, полисами и т.п.)
        # А потом, к полученному результату (уже урезанному за счет join-условий), будут присоеденены таблица дубликатов Client с использованием
        # уже сформированного условия clientJoinCond, которое так же минимизирует результат,
        # а уже после будут присоединены доп. таблицы с данными по дубликату (так же с условиями, сформированными ранее).
        clientJoinCond = [self.tableClient['deleted'].eq(0),
                          self.tableDuplicateClient['deleted'].eq(0)
                          ]

        if self.clientId():
            clientJoinCond.append(self.tableClient['id'].eq(self.clientId()))
            clientJoinCond.append(self.tableDuplicateClient['id'].ne(self.tableClient['id']))
        else:
            clientJoinCond.append(self.tableDuplicateClient['id'].gt(self.tableClient['id']))

        self.step(0, 3, u'Формирование запроса')
        # Обработка опции поиска дубликатов по ФИО
        if self.chkName.isChecked():
            # Получение значения допустимого расхождения в написании (максимальное растояние Дамерау-Левенштейна) для Ф.И.О.
            precision = self.spbNameComparisonPrecision.value()

            # При допустимом расхождении меньше или равном нулю считать, что требуется сравнение строк на строгое равенство
            if precision <= 0:
                clientJoinCond.append(self.getField('lastName', True).eq(self.getField('lastName', False)))
                clientJoinCond.append(self.getField('firstName', True).eq(self.getField('firstName', False)))

                # Если у основного пациента или у предполагаемого дубликата нет отчества, то не сравнивать по отчеству
                clientJoinCond.append(db.joinOr([self.getField('patrName', True).eq(''),
                                                 self.getField('patrName', False).eq(''),
                                                 self.getField('patrName', True).eq(self.getField('patrName', False))
                                                 ]))
            else:
                # atronah: для уменьшения количества вызовов функции расчета растояния Дамерау-Левенштейна
                # Ф.И.О. сравниваемых пациентов объединяются в одну строку и эти две строки сравниваются
                # с утроеной точностью, если есть отчество у обоих, иначе с удвоеной

                # условие наличия отчества у обоих пациентов (базового и дубликата)
                patrNameExistsTemplate = '%s AND %s' % (self.getField('patrName', True).name(),
                                                      self.getField('patrName', False).name())

                # шаблон для формирования одной строки из Ф.И.О. с учетом наличия отчества
                nameTemplate = u'CONCAT_WS(\' \', %s, %s, IF(%s, %s, \'\'))'

                baseName = nameTemplate % (self.getField('lastName', True).name(),
                                           self.getField('firstName', True).name(),
                                           patrNameExistsTemplate,
                                           self.getField('patrName', True).name())
                dupName = nameTemplate % (self.getField('lastName', False).name(),
                                           self.getField('firstName', False).name(),
                                           patrNameExistsTemplate,
                                           self.getField('patrName', False).name())
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d * IF(%s, 3, 2))' % (baseName,
                                                                          dupName,
                                                                          precision,
                                                                          patrNameExistsTemplate))

        # Список опций поиска (с одинаковым алгоритмом обработки)
        filterInfoList = [('sex', self.chkSex, None),
                          ('birthDate', self.chkBirthDate, None),
                          ('birthPlace', self.chkBirthPlace, self.spbBirthPlaceComparisonPrecision),
                          ('SNILS', self.chkSNILS, self.spbSNILSComparisonPrecision),
                          ('createDatetime', self.chkCreateDate, None)]

        # Обработка опций поиска дубликатов
        for fieldName, chkWidget, precisionWidget in filterInfoList:
            self.showedColumns.append(fieldName)
            cols.append(self.getFieldDescription(fieldName, True))
            cols.append(self.getFieldDescription(fieldName, False))
            if chkWidget.isChecked():
                precision = precisionWidget.value() if precisionWidget else 0
                if precision <= 0:
                    clientJoinCond.append(self.getField(fieldName, True).eq(self.getField(fieldName, False)))
                    if fieldName == 'SNILS':
                        clientJoinCond.append(self.getField(fieldName, True).ne(u''))
                else:
                    queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.getField(fieldName, True).name(), self.getField(fieldName, False).name(), precision))
        # -- КОНЕЦ -- Определение условий соединения таблицы Client с самой собой



        # Присоединение второй таблицы Client AS DuplicateClient (таблицы дубликатов) производится позже, чтобы
        # к тому времени, за счет INNER JOIN'ов вспомогательных таблиц
        # уменьшить количество строк в первой таблицы Client (таблицы основных пациентов)



        # -- НАЧАЛО -- Формирование списка условий для последующего (после присоединения таблицы дубликатов)
        # присоединения вспомогательных таблиц с инфой о дубликате. А так же присоединения таких таблиц для основного пациента.

        # Список условий для присоединения данных о гражданстве потенциального дубликата
        duplicateSocStatusJoinCond = []
        if self.chkCitizenship.isChecked():
            cols.append(self.getFieldDescription('citizenship', True))
            cols.append(self.getFieldDescription('citizenship', False))
            # Получение списка классов соц.статусов, имеющих отношение к гражданству (собственно, само "гражданство" и его подгруппы)
            citizenshipClassIdList = db.getDescendants(self.tableRBSocStatusClass,
                                                       self.tableRBSocStatusClass['group_id'],
                                                       forceRef(db.translate(self.tableRBSocStatusClass,
                                                                             self.tableRBSocStatusClass['code'],
                                                                             '8',
                                                                             self.tableRBSocStatusClass['id'])))

            # Присоединение таблицы с данными о гражданстве основного пациента
            queryTable = queryTable.innerJoin(self.tableClientSocStatus, [self.tableClientSocStatus['client_id'].eq(self.tableClient['id']),
                                                                          self.tableClientSocStatus['deleted'].eq(0),
                                                                          self.tableClientSocStatus['socStatusClass_id'].inlist(citizenshipClassIdList)])
            queryTable = queryTable.innerJoin(self.tableClientSocStatusType, self.tableClientSocStatusType['id'].eq(self.tableClientSocStatus['socStatusType_id']))

            # Заполнение условия присоединение таблицы с данными о гражданстве потенциального дубликата
            duplicateSocStatusJoinCond = [self.tableDuplicateClientSocStatus['client_id'].eq(self.tableDuplicateClient['id']),
                                          self.tableDuplicateClientSocStatus['deleted'].eq(0),
                                          self.tableDuplicateClientSocStatus['socStatusClass_id'].inlist(citizenshipClassIdList),
                                          self.tableDuplicateClientSocStatus['socStatusType_id'].eq(self.tableClientSocStatus['socStatusType_id'])]  # <-- проверка на дубли по гражданству при джойне


        if not self.isFromRegistry:
            cols.append(self.getFieldDescription('document', True))
            cols.append(self.getFieldDescription('document', False))
            self.showedColumns.append('document')
            # id группы документов "удостоверение личности"
            mainDocumentTypeGroupId = forceRef(db.translate('rbDocumentTypeGroup', 'code', '1', 'id'))
            # список типов документов, относящихся к группе "удостоверение личности"
            documentTypeIdList = db.getIdList('rbDocumentType',
                                              idCol = 'id',
                                              where = 'group_id = %s' % mainDocumentTypeGroupId)
            # Список условий для присоединения данных о документах потенциального дубликата
            duplicateDocumentsJoinCond = [self.tableDuplicateClientDocument['client_id'].eq(self.tableDuplicateClient['id']),
                                          self.tableDuplicateClientDocument['deleted'].eq(0),
                                          self.tableDuplicateClientDocument['documentType_id'].eq(self.tableClientDocument['documentType_id'])]
            queryCond.append(db.joinOr([self.tableClientDocument['id'].isNull(),
                                        self.tableClientDocument['documentType_id'].inlist(documentTypeIdList)]))
        if self.chkDocuments.isChecked():
            queryTable = queryTable.innerJoin(self.tableClientDocument, [self.tableClientDocument['client_id'].eq(self.tableClient['id']),
                                                                         self.tableClientDocument['deleted'].eq(0)
                                                                         ])

            precision = self.spbDocumentComparisonPrecision.value()
            if precision <= 0:
                duplicateDocumentsJoinCond.append(self.tableDuplicateClientDocument['serial'].eq(self.tableClientDocument['serial']))
                duplicateDocumentsJoinCond.append(self.tableDuplicateClientDocument['number'].eq(self.tableClientDocument['number']))
            else:
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.tableDuplicateClientDocument['serial'].name(), self.tableClientDocument['serial'].name(), precision))
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.tableDuplicateClientDocument['number'].name(), self.tableClientDocument['number'].name(), precision))
        else:
            queryTable = queryTable.leftJoin(self.tableClientDocument, [self.tableClientDocument['client_id'].eq(self.tableClient['id']),
                                                                        self.tableClientDocument['deleted'].eq(0),
                                                                        db.joinOr((
                                                                            self.tableClientDocument['endDate'].gt(db.now()),
                                                                            self.tableClientDocument['endDate'].isNull()
                                                                        ))])


        # Список условий для присоединения данных о полисе потенциального дубликата
        duplicatePolicyJoinCond = []
        if self.chkPolicy.isChecked():
            cols.append(self.getFieldDescription('policy', True))
            cols.append(self.getFieldDescription('policy', False))
            self.showedColumns.append('policy')
            queryTable = queryTable.innerJoin(self.tableClientPolicy, [self.tableClientPolicy['client_id'].eq(self.tableClient['id']),
                                                                  self.tableClientPolicy['deleted'].eq(0)])

            duplicatePolicyJoinCond = [self.tableDuplicateClientPolicy['client_id'].eq(self.tableDuplicateClient['id']),
                                       self.tableDuplicateClientPolicy['deleted'].eq(0),
                                       self.tableDuplicateClientPolicy['policyType_id'].eq(self.tableClientPolicy['policyType_id'])]

            precision = self.spbDocumentComparisonPrecision.value()
            if precision <= 0:
                duplicatePolicyJoinCond.append(self.tableDuplicateClientPolicy['serial'].eq(self.tableClientPolicy['serial']))
                duplicatePolicyJoinCond.append(self.tableDuplicateClientPolicy['number'].eq(self.tableClientPolicy['number']))
            else:
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.tableDuplicateClientPolicy['serial'].name(), self.tableClientPolicy['serial'].name(), precision))
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.tableDuplicateClientPolicy['number'].name(), self.tableClientPolicy['number'].name(), precision))

        # Список условий для присоединения данных об адресе проживания потенциального дубликата
        duplicateLocAddressJoinCond = []
        if self.chkLocAddress.isChecked():
            cols.append(self.getFieldDescription('locAddress', True))
            cols.append(self.getFieldDescription('locAddress', False))
            self.showedColumns.append('locAddress')

            queryTable = queryTable.innerJoin(self.tableClientLocAddress, [self.tableClientLocAddress['client_id'].eq(self.tableClient['id']),
                                                                           self.tableClientLocAddress['deleted'].eq(0),
                                                                           self.tableClientLocAddress['type'].eq(1)])

            duplicateLocAddressJoinCond.append(self.tableDuplicateClientLocAddress['client_id'].eq(self.tableDuplicateClient['id']))
            duplicateLocAddressJoinCond.append(self.tableDuplicateClientLocAddress['deleted'].eq(0))

            precision = self.spbLocAddressComparisonPrecision.value()
            if precision <= 0:
                duplicateLocAddressJoinCond.append(self.getField('locAddress', True).eq(self.getField('locAddress', False)))
            else:
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.getField('locAddress', True).name(),
                                                                                            self.getField('locAddress', False).name(),
                                                                                            precision))

        # Список условий для присоединения данных об адресе регистрации потенциального дубликата
        duplicateRegAddressJoinCond = []
        if self.chkRegAddress.isChecked():
            cols.append(self.getFieldDescription('regAddress', True))
            cols.append(self.getFieldDescription('regAddress', False))
            self.showedColumns.append('regAddress')

            queryTable = queryTable.innerJoin(self.tableClientRegAddress, [self.tableClientRegAddress['client_id'].eq(self.tableClient['id']),
                                                                           self.tableClientRegAddress['deleted'].eq(0),
                                                                           self.tableClientRegAddress['type'].eq(1)])

            duplicateRegAddressJoinCond.append(self.tableDuplicateClientRegAddress['client_id'].eq(self.tableDuplicateClient['id']))
            duplicateRegAddressJoinCond.append(self.tableDuplicateClientRegAddress['deleted'].eq(0))

            precision = self.spbRegAddressComparisonPrecision.value()
            if precision <= 0:
                duplicateRegAddressJoinCond.append(self.getField('regAddress', True).eq(self.getField('regAddress', False)))
            else:
                queryCond.append('checkDamerauLevenshtein(%s, %s, %d)' % (self.getField('regAddress', True).name(),
                                                                                            self.getField('regAddress', False).name(),
                                                                                            precision))

        # -- КОНЕЦ -- Формирование списка условий ...

        onlyBaseClientQueryTable = queryTable

        queryTable = queryTable.innerJoin(self.tableDuplicateClient, clientJoinCond)
        if self.chkCitizenship.isChecked():
            queryTable = queryTable.innerJoin(self.tableDuplicateClientSocStatus, duplicateSocStatusJoinCond)

        if self.chkDocuments.isChecked():
            queryTable = queryTable.innerJoin(self.tableDuplicateClientDocument, duplicateDocumentsJoinCond)
        elif not self.isFromRegistry:
            queryTable = queryTable.leftJoin(self.tableDuplicateClientDocument, duplicateDocumentsJoinCond)

        if self.chkPolicy.isChecked():
            queryTable = queryTable.innerJoin(self.tableDuplicateClientPolicy, duplicatePolicyJoinCond)

        if self.chkLocAddress.isChecked():
            queryTable = queryTable.innerJoin(self.tableDuplicateClientLocAddress, duplicateLocAddressJoinCond)

        if self.chkRegAddress.isChecked():
            queryTable = queryTable.innerJoin(self.tableDuplicateClientRegAddress, duplicateRegAddressJoinCond)
        
        currentStep = 1
        stepCount = 1
        
        if self.chkOneQueryByClient.isChecked():
            if not self.uncompletedIdList:
                self.step(0, 1, u'Получение списка всех пациентов...')
                self.uncompletedIdList = db.getDistinctIdList(onlyBaseClientQueryTable, 
                                                              idCol = self.tableClient['id'],
                                                              where = [self.tableClient['deleted'].eq(0)]) if not self.clientId() else [self.clientId()]
                self.completedIdList = []
            
            stepCount = len(self.uncompletedIdList)
            self.step(0,
                      max(stepCount, 1), 
                      u'Обработанно пациентов %d из %d' % (len(self.completedIdList), len(self.uncompletedIdList)))
            while self.uncompletedIdList:
                if self._abort:
                    break
                baseClientId = self.uncompletedIdList.pop()
                baseClientCond = [self.tableClient['id'].eq(baseClientId)]
                if len(self.completedIdList) < len(self.uncompletedIdList):
                    baseClientCond.append(self.tableDuplicateClient['id'].notInlist(self.completedIdList) if self.completedIdList else '1')
                else:
                    baseClientCond.append(self.tableDuplicateClient['id'].inlist(self.uncompletedIdList) if self.uncompletedIdList else '1')
                                  
                clientRecordList = db.getRecordList(queryTable, cols, where = baseClientCond + queryCond)
                for record in clientRecordList:
                    self.addClientInfo(record)
                
                # Добавляем id пациента в список обработанных на случай, если у него не было найдено дубликатов и в этот список его его не добавила функция addClientInfo
                self.completedIdList.append(baseClientId)
                currentStep = len(self.completedIdList)
                self.step(currentStep, 
                          stepCount,
                          u'Обработанно пациентов %d из %d' % (currentStep, stepCount))
        else:
            self.completedIdList = []
            
            self.step(0, 1, u'Выполнение запроса')
            QtGui.qApp.processEvents()
            duplicatesRecords = db.getRecordList(queryTable, cols=cols, where=queryCond, order=self.getAlias('code', True))
            
            stepCount = len(duplicatesRecords) + 1
            currentStep = 0
            self.step(currentStep, stepCount, u'Обработка полученных данных')
            record = QtSql.QSqlRecord()
            for record in duplicatesRecords:
                if self._abort:
                    break
                
                self.addClientInfo(record)
                
                currentStep += 1
                self.step(currentStep, stepCount, u'Обработка полученных данных')
        currentStep = stepCount
        self.step(currentStep, stepCount, u'Поиск дубликатов завершен')

        self.btnPrint.setEnabled(True)
    
    
    def addClientInfo(self, record): # baseClientId, duplicateClientId = None):
        isWorkWithBaseClientList = [True, False]
        # Добавляем информацию о дубликате и о базовом (если еще не добавляли)
        for isWorkWithBaseClient in isWorkWithBaseClientList:
            clientId = forceRef(record.value(self.getAlias('code', isWorkWithBaseClient)))
            
            baseClientId = clientId if isWorkWithBaseClient else forceRef(record.value(self.getAlias('code', True)))
            duplicateClientId = clientId
            
            
            if not isWorkWithBaseClient and clientId in self.completedIdList:
                continue
            
            
            clientInfo = {}
            for key in self._fieldsInfo.keys():
                alias = self.getAlias(key, isWorkWithBaseClient)
                if not record.contains(alias):
                    continue
                clientInfo[self.getAlias(key, False)] = forceString(record.value(alias))
                
            if isWorkWithBaseClient:
                self.clientsInfo.setdefault(clientId, {}).update(clientInfo)
            
            
            if clientId in self.completedIdList:
                continue

            self.clientsInfo.setdefault(baseClientId, {}).setdefault('clientInfoList', {}).setdefault(duplicateClientId, {}).update(clientInfo)
        
            if clientId not in self.completedIdList:
                self.completedIdList.append(clientId)
            
            if clientId in self.uncompletedIdList:
                self.uncompletedIdList.remove(clientId)

    
    
    def updateModels(self):
        self.baseClientModel.setSourceDict(self.clientsInfo, sortKey = self.getAlias('name', False))
#         self.tblBaseClient.resizeColumnsToContents()
        
        self.duplicateModel.clearColumnInfo()        
        for key in sorted(self._fieldsInfo.keys(), key = lambda key : self._fieldsInfo[key]['sortIndex']):
            alias = self.getAlias(key, False)
            if key not in self.showedColumns:
                continue
            self.duplicateModel.addCollumnInfo(alias, self._fieldsInfo[key].get('header', ''))   
        
        idx = self.tblBaseClient.model().index(0, 0)
        self.tblBaseClient.setCurrentIndex(idx)
        self.tblBaseClient.setSelectedRowList([0])
        self.on_tblBaseClient_clicked(idx)
        
        self.lblCountRecords.setText('%s/%s' % (self.baseClientModel.rowCount(),
                                                len(self.completedIdList)))


    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        self.printDuplicatesList()

    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblBaseClient_clicked(self, index):
        rowDict = self.baseClientModel.getRowDict(index.row())
        alias = self.getAlias('code', False)
        self.duplicateModel.setHighlightRows(alias, rowDict.get(alias, -1))
        self.duplicateModel.setSourceDict(rowDict.get('clientInfoList', {}), sortKey = self.getAlias('name', False))
        duplicateCount = self.duplicateModel.rowCount()
        self.actChangeBaseClient.setEnabled(duplicateCount > 1)
        self.actMergeAllToBase.setEnabled(duplicateCount > 1)
#         self.tblDuplicateClient.resizeColumnsToContents()
    
    
    @QtCore.pyqtSlot()
    def changeBaseClient(self):
        baseIndex = self.tblBaseClient.currentIndex()
        if not baseIndex.isValid():
            return
        
        baseRow = baseIndex.row()
        baseDict = self.baseClientModel.getRowDict(baseRow)
        if not baseDict:
            return
#         baseId = baseDict.get(self.getAlias('code', None))
        dupRow = self.tblDuplicateClient.currentIndex().row()
        dupDict = self.duplicateModel.getRowDict(dupRow)
#         dupId = dupDict.get(self.getAlias('code', False))

        baseClientInfo = dict(baseDict)
        if baseClientInfo.has_key('clientInfoList'):
            baseClientInfo.pop('clientInfoList')
        baseDict.update(dupDict)
        self.baseClientModel.updateRowKey(baseRow, forceInt(baseDict[self.getAlias('code', False)]))
        dupDict.update(baseDict)
        
        self.baseClientModel.reset()
        self.tblBaseClient.setCurrentIndex(baseIndex)
        self.on_tblBaseClient_clicked(baseIndex)
    

    def printDuplicatesList(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Список найденных двойников\n')
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'Параметры поиска:\n')
        cursor.insertBlock()
        columns = [
            ('25?', [u'Фильтр'], CReportBase.AlignLeft),
            ('50?', [u'Максимальная степень расхождения, букв'], CReportBase.AlignCenter)
        ]
        usedFiltersTable = createTable(cursor, columns, headerRowCount=len(self._usedFilters) + 1, border=0.5)
        for i, filterIdx in enumerate(self._usedFilters):
            chkBox, widget = self._filters[filterIdx]
            filterName = chkBox.text()
            filterPrecision = ''
            if not widget is None:
                filterPrecision = '%d' % widget.value() if widget.value() else u'строгое равенство'
            usedFiltersTable.setText(i + 1, 0, filterName)
            usedFiltersTable.setText(i + 1, 1, filterPrecision)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.TableBody)

        columnWidth = '%.4f%%' % (100.0 / len(self.showedColumns))
        tableColumns = [(columnWidth, self._fieldsInfo[col].get('header', ''), CReportBase.AlignLeft) for col in self.showedColumns]
        columnNumber = dict([(name, index) for index, name in enumerate(self.showedColumns)])

        table = createTable(cursor, tableColumns)

        for r in xrange(self.baseClientModel.rowCount()):
            rowDict = self.baseClientModel.getRowDict(r)
            clientInfoList = rowDict.get('clientInfoList', {})
            if clientInfoList:
                i = table.addRow()
                table.mergeCells(i, 0, 1, len(tableColumns))
                for dupId, dupInfo in [(id, clientInfoList[id]) for id in sorted(clientInfoList, key=lambda k: clientInfoList[k].get('name', ''))]:
                    i = table.addRow()
                    for colIndex, colName in enumerate(self.showedColumns):
                        table.setText(i, colIndex, dupInfo.get(colName, ''))
                    table.setText(i, columnNumber['code'], dupId)

        html = doc.toHtml(QtCore.QByteArray('utf-8'))
        view = CReportViewDialog(self)
        view.btnShowQuery.setEnabled(False)
        view.setText(html)
        view.exec_()

    def step(self, currentStep, maxStep, message = 'Обработка данных...'):
        if self.prbControlDoubles.maximum() != maxStep:
            self.prbControlDoubles.setRange(0, maxStep)
        self.prbControlDoubles.setValue(currentStep)
        self.prbControlDoubles.setFormat('%s (%%p%%)' % message)
        QtGui.qApp.processEvents()
    
    
    def saveLog(self, fileName, errorLogList=None, workLogList=None):
        if not errorLogList:
            errorLogList = []
        if not workLogList:
            workLogList = []
        with codecs.open(fileName, 'a', encoding = 'utf8') as logFile:
            for logLine in workLogList:
                logFile.write(logLine)
                logFile.write(os.linesep)
            for logLine in errorLogList:
                logFile.write(logLine)
                logFile.write(os.linesep)
        
    
    
    @QtCore.pyqtSlot()
    def mergeAllToBase(self):        
        if self.baseClientModel.rowCount() <= 0:
            QtGui.QMessageBox.warning(self,
                                u'Внимание', 
                                u'Нечего объединять\nСписок пациентов, у которых есть дубликаты - пуст', 
                                QtGui.QMessageBox.Ok)
            return False
        
        if self.duplicateModel.rowCount() <= 1:
            QtGui.QMessageBox.warning(self,
                                u'Внимание', 
                                u'Нечего объединять\nСписок дубликатов выбранного пациента пуст или содержит только одного пациента', 
                                QtGui.QMessageBox.Ok)
            
        if QtGui.QMessageBox.No == QtGui.QMessageBox.question(self,
                                                  u'Подтвердите начало объединения', 
                                                  u'Вы уверены, что хотите объединить выбранную группу пациентов,\nиспользуя в качестве базового - пациента, выделенного зеленым?', 
                                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                  QtGui.QMessageBox.No):
            return False
            
            
        self._abort = False
        self.btnBeginCheck.setEnabled(False)
        outXMLFile = None
        try:
            baseIndex = self.tblBaseClient.currentIndex()
            baseRow = baseIndex.row()
            baseDict = self.baseClientModel.getRowDict(baseRow)
            baseClientId = self.baseClientModel.getRowKey(baseRow)
            if not baseClientId:
                QtGui.QMessageBox.warning(self,
                                    u'Внимание', 
                                    u'Базовый пациент имеет некорректный код: %s' % baseClientId, 
                                    QtGui.QMessageBox.Ok)
                return False
            
            orgId = QtGui.qApp.currentOrgId()
            orgCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', orgId, 'miacCode'))
            
            currentTimeString = forceString(QtCore.QDateTime.currentDateTime().toString('ddMMyyyy_hh-mm-ss'))
            
            logFileName = os.path.join(self.templateDir(), u'duplicateMergeLog_c%s_%s.log' % (baseClientId, currentTimeString))
            
            xmlLogFileName = os.path.join(self.templateDir(), u'duplicateMergeLog_c%s_%s.xml' % (baseClientId, currentTimeString))
            outXMLFile = QtCore.QFile(xmlLogFileName)
            outXMLFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
            xmlWriter = QtCore.QXmlStreamWriter(outXMLFile)
            xmlWriter.setAutoFormatting(True)
            xmlWriter.writeStartDocument()
            xmlWriter.writeStartElement('DUPS')
            
            clientInfoList = baseDict.get('clientInfoList', {})
            duplicateIdList = clientInfoList.keys()
            workLogList = self.mergeClientsCommon(baseClientId, duplicateIdList)
            if not workLogList is None:
                self.saveLog(self.commonLogFileName, workLogList=workLogList)
            for duplicateId in duplicateIdList:
                duplicateId = duplicateId
                if baseClientId == duplicateId:
                    self.duplicateModel.removeKey(duplicateId)
                    self.duplicateModel.reset()
                    continue
                Logger.logDeletedDouble(baseClientId, duplicateId)
                errorLogList, workLogList = self.mergeClients(baseClientId, duplicateId, self.step)
                xmlWriter.writeEmptyElement('Duplicate')
                xmlWriter.writeAttribute('lpu', orgCode)
                xmlWriter.writeAttribute('baseId', forceStringEx(baseClientId))
                xmlWriter.writeAttribute('dupId', forceStringEx(duplicateId))
                self.saveLog(logFileName, errorLogList, workLogList)
                if errorLogList:
                    QtGui.QMessageBox.critical(self,
                                         u'Ошибка!!!', 
                                         u'\n'.join(errorLogList), 
                                         QtGui.QMessageBox.Ok)
                    return False
                
                self.duplicateModel.removeKey(duplicateId)
                self.duplicateModel.reset()
            
            xmlWriter.writeEndElement()
            xmlWriter.writeEndDocument()
            
            
            self.baseClientModel.removeKey(baseClientId)
            self.baseClientModel.reset()
            self.tblBaseClient.setCurrentIndex(baseIndex)

        finally:
            self.btnBeginCheck.setEnabled(True)
            self.updateModels()

            if outXMLFile:
                outXMLFile.close()
        
    @staticmethod
    def mergeClientsCommon(baseClientId, duplicateClientIdList):
        if baseClientId and duplicateClientIdList:
            db = QtGui.qApp.db
            workLogMessageList = []
            currentTimeString = forceString(QtCore.QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm:ss'))
            userLogin = forceString(db.translate('Person', 'id', QtGui.qApp.userId, 'login'))
            duplicateClientIdList.remove(baseClientId)
            workLogMessageList.append(u'[%s пользователь: %s] базовый пациент: %s -> дубликаты: %s' %(currentTimeString, userLogin, baseClientId, ', '.join(forceString(duplicateClientId) for duplicateClientId in duplicateClientIdList)))
            return workLogMessageList
        else:
            return None
        
        
    ## Функция объединения двух пациентов (данных по ним)
    # @param baseClientId: id основного/базового пациента, который будет оставлен в системе/бд и на которого будут "перенесены" все данные дубликата 
    # @param duplicateClientId: id дубликата, который будет удален из системы/бд после того, как его данные будут пересены на основного пациента
    # @param stepFunction: (необязательный параметр) указатель на функцию с параметрами 
    # (<текущий_шаг_операции>, <общее_количество_операций>, <название_выполняемой_операции>)
    # которая позволяет передавать внешнему алгоритму информацию о текущем состоянии процесса объединения путем вызова этой функции внутри алгоритма объединения
    # @return (errorMessageList, workLogMessageList)
    #    где errorMessageList - это список(list) со строками, описывающими возникшие в ходе объединения ошибками, 
    #            если не пустой, то алгоритм завершился раньше времени и с ошибками
    #        workLogMessageList - список со строками, содержащими подробное описание каждого шага процесса объединения, 
    #            с указанием временых меток и доп. информации по обрабатываемым данным.
    #
    # --- Возможные и пока не учтенные проблемы:
    # 1) Пересекающиеся и не совместимые события
    # 2) Отсутствие номерка эл. очереди у основного пациента и наличие такого номерка у дубликата.
    @staticmethod
    def mergeClients(baseClientId, duplicateClientId, stepFunction = None):
        db = QtGui.qApp.db
        
        currentStep = [0]
        maxStep = 0 # пока не известно.. Перерасчитывается после определения таблиц, с которым будет производиться работа и до инициализирующего шага(step'a)
        
        workLogMessageList = []
        
        def logOperation(operationMessage):
            currentTimeString = forceString(QtCore.QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm:ss'))
            workLogMessageList.append(u'[%s] %s' %(currentTimeString, operationMessage))
        #end of logOperation
        
        
        def step(message):
            if callable(stepFunction):
                stepFunction(currentStep[0], maxStep, message)
            logOperation(message)
            currentStep[0] += 1
        #end of step
        
                
        errorMessageList = []
        
        if not baseClientId:
            errorMessageList.append(u'Ошибочно указан основной пациент (id = %s)' % baseClientId)
        if not duplicateClientId:
            errorMessageList.append(u'Ошибочно указан дубликат (id = %s)' % duplicateClientId)
        if baseClientId == duplicateClientId:
            errorMessageList.append(u'Одинаковый id у базового пациента и дубликата (id = %s)' % duplicateClientId)
            
        
        if errorMessageList:
            return errorMessageList, workLogMessageList
        
        
        
        
        tableClient = db.table('Client')
        tableClientAddress = db.table('ClientAddress')
        tableClientAllergy = db.table('ClientAllergy')
        tableClientAttach = db.table('ClientAttach')
        tableClientContact = db.table('ClientContact')
        tableClientDocument = db.table('ClientDocument')
        tableClientFakeSNILS = db.table('ClientFakeSNILS')
        tableClientFile = db.table('ClientFile')
        tableClientIdentification = db.table('ClientIdentification')
        tableClientPolicy = db.table('ClientPolicy')
        tableClientQueueNumber = db.table('ClientQueueNumber')
        tableClientRelation = db.table('ClientRelation')
        tableClientSocStatus = db.table('ClientSocStatus')
        tableClientWork = db.table('ClientWork')
        tableClientInfoSource = db.table('ClientInfoSource')

        tableContract = db.table('Contract')
        tableContractContingent = db.table('Contract_Contingent')
        tableDeferredQueue = db.table('DeferredQueue')
        tableDiagnosis = db.table('Diagnosis')
        tableEvent = db.table('Event')
        tableReferral = db.table('Referral')
        tableTakenTissueJournal = db.table('TakenTissueJournal')
        tableTempInvalid = db.table('TempInvalid')

        # Список таблиц, в которых необходима простая замена ссылки на дубликата ссылкой на базового пациента.
        # формат элементов списка: (таблица,_базы, имя_поля_ссылки, название_сущности_в_род_падеже)
        tableListForSimpleUpdate =[(tableEvent, 'client_id', u'обращений'),
                                   (tableDiagnosis, 'client_id', u'диагнозов'),
                                   (tableContract, 'assignedClient_id', u'именных договоров'),
                                   (tableContractContingent, u'client_id', u'контингентов договоров'),
                                   (tableClientFile, 'client_id', u'файлов'),
                                   (tableClientIdentification, 'client_id', u'учетных номеров'),
                                   (tableDeferredQueue, 'client_id', u'записей ЖОС'),
                                   (tableReferral, 'client_id', u'направлений'),
                                   (tableTakenTissueJournal, 'client_id', u'операций по забору тканей'),
                                   (tableTempInvalid, 'client_id', u'случаев ВУТ/инвалидности/ограничений жизнедеятельности')
                                   ]
        
        # Список таблиц, в которых необходимо найти записи основного пациента 
        # и добавить к ним записи дубликата, у которых указанные поля содержат значения, отличные от значений в записях основного пациента.
        # Проще говоря, перенос на основного пациента записей дубликата только того типа, которого еще не было у базового.
        tableListForConditionalUpdate = [# Перенесет все адреса дубликата с типом, отстуствующим у базового, а оставшиеся адреса дубликата удалит.
                                         (tableClientAddress, 'client_id', ['type'], u'адресов'),
                                         # Перенесет все аллергии дубликата на веществом, аллергия на которого отсутствует у базового, а остальные удалит
                                         (tableClientAllergy, 'client_id', ['nameSubstance'], u'аллергических непереносимостей'),
                                         # Перенесет все прикрепления дубликата с типом, отстутствующим у базового, а остальные удалит
                                         (tableClientAttach, 'client_id', ['attachType_id'], u'прикреплений'),
                                         # Перенесет все контакты дубликата с типом, отстутствующим у базового, а остальные удалит
                                         (tableClientContact, 'client_id', ['contactType_id'], u'контактов'),
                                         # Перенесет все документы дубликата с типами, отстуствующими у базового, а остальные удалит
                                         (tableClientDocument, 'client_id', ['documentType_id'], u'документов'),
                                         # Перенесет все полисы дубликата с типом и видом, отсутствующим у базового, а остальные удалит
                                         (tableClientPolicy, 'client_id', ['policyType_id', 'policyKind_id'], u'полисов'),
                                         # Перенесет все прямые связи дубликата с др. пациентами, с которыми не связан базовый и удалит все остальные связи дубликата
                                         (tableClientRelation, 'client_id', ['relative_id'], u'прямых связей'),
                                         # Перенесет все обратные связи дубликата с др. пациентами, с которыми не связан базовый и удалит все остальные связи дубликата
                                         (tableClientRelation, 'relative_id', ['client_id'], u'обратных связей'),
                                         # Перенесет соц.статусы дубликата с классом и типом, отсутствующим у базового пациента, остальные удалит
                                         (tableClientSocStatus, 'client_id', ['socStatusClass_id', 'socStatusType_id'], u'соц.статусов'),
                                         # Перенесет места работы дубликата в тех организациях, в которых базовый пациент не работал и удалит остальные места работы дубликата
                                         (tableClientWork, 'client_id', ['org_id'], u'мест работы'),
                                         # Перенесёт фейковый СНИЛС, если у пациента такого нет
                                         (tableClientFakeSNILS, 'client_id', ['fakeSNILS'], u'фейковых СНИЛСов'),
                                         # Перенесет новые источники информации, если у пациента нет таких
                                         (tableClientInfoSource, 'client_id', ['rbInfoSource_id'], u'источников информации о ЛПУ'),
        ]
        
        # Список таблиц, в которых надо просто удалить все записи, связанные с дубликатом.
        tableListForDelete = [# Удалит все номерки эл. очереди, связанные с дубликатом.
                              (tableClientQueueNumber, 'client_id', u'номерков эл.очереди')]
        
        
        # Количество шагов, которые будут проделаны, равно сумме из
        # 1 - первый, инициализирующий шаг
        # 2 * количества таблиц на простое обновление (в обработчике каждой таблицы два шага: получение и обработка данных)
        # 2 * количество таблиц на условное обновление
        # 2 * количество таблиц на простое удаление
        # 1 - удаление дубликата из таблицы Client
        maxStep = 1 + 2 * len(tableListForSimpleUpdate) + 2 * len(tableListForConditionalUpdate) + 2 * len(tableListForDelete)
        
        step(u'Инициализация слияния пациента %d (базовый) и %d (дубликат)' % (baseClientId, duplicateClientId))
        
        for table, clientCol, description in tableListForSimpleUpdate:
            step(u'Получение списка %s дубликата из таблицы %s' % (description, table.name()))
            dataRecords = db.getRecordList(table, '*', where = [table[clientCol].eq(duplicateClientId)])
            
            step(u'Перенос %d %s дубликата на базового пациента' % (len(dataRecords), description))
            updatedIdList = []
            db.transaction()
            try:
                for record in dataRecords:
                    record.setValue(clientCol, QtCore.QVariant(baseClientId))
                    updatedIdList.append(db.updateRecord(table, record))
                db.commit()
                if updatedIdList:
                    logOperation(u'В таблице "%s" обновлено поле "%s" (%s -> %s) для записей с id из списка %s' % (table.name(),
                                                                                                              clientCol,
                                                                                                              duplicateClientId, 
                                                                                                              baseClientId,
                                                                                                              updatedIdList))
            except Exception, e:
                db.rollback()
                errorMessageList.append(u'Ошибка обновления записей в таблице "%s" (%s)' % (table.name(), e))
                return errorMessageList, workLogMessageList


        for table, clientCol, compareFieldList, description in tableListForConditionalUpdate:
            step(u'Получение списков %s основного пациента и дубликата из таблицы %s' % (description, table.name()))
            dataRecords = db.getRecordList(table, compareFieldList, where = [table[clientCol].eq(baseClientId)])

            existedDataCond = [] # Условие соответствия записей по указанным в compareFieldList полям
            for record in dataRecords:
                values = []
                for fieldName in compareFieldList:
                    values.append(table[fieldName].eq(record.value(fieldName)))
                existedDataCond.append(db.joinAnd(values))

            # в итоге existedDataCond содержит условия, соблюдение которых для записи дубликата означает, что у базового пациента есть эти же данные
            # (например, если table = ClientDocument, а compareFieldList = ['documentType_id'], то полученное условие позволит выявить все документы того же типа)

            existedInDuplicateCond = [
                table[clientCol].eq(duplicateClientId),
                db.joinOr(existedDataCond)
            ]
            if table is tableClientPolicy:
                existedInDuplicateCond.append(u'NOT {0}'.format(db.existsStmt(tableEvent, [tableEvent['deleted'].eq(0),
                                                                                           tableEvent['clientPolicy_id'].eq(tableClientPolicy['id'])])))

            existedIdList = db.getIdList(table, where=existedInDuplicateCond) if existedDataCond else []

            dataRecords = db.getRecordList(table, '*', where=[table[clientCol].eq(duplicateClientId),
                                                              table.idField().notInlist(existedIdList) if existedIdList else '1'])
            step(u'Перенос %d %s дубликата, отсутствующих у основного пациента и удаление %d уже имеющихся' % (len(dataRecords), description, len(existedIdList)))
            updatedIdList = []
            db.transaction()
            try:
                for record in dataRecords:
                    record.setValue(clientCol, toVariant(baseClientId))
                    updatedIdList.append(db.updateRecord(table, record))

                db.deleteRecord(table, [table.idField().inlist(existedIdList)])

                db.commit()
                if updatedIdList:
                    logOperation(u'В таблице "%s" обновлено поле "%s" (%s -> %s) для записей с id из списка %s' % (table.name(), clientCol, duplicateClientId, baseClientId, updatedIdList))
                if existedIdList:
                    logOperation(u'В таблице "%s" удалены записи с id из списка %s' % (table.name(), existedIdList))
            except Exception, e:
                db.rollback()
                errorMessageList.append(u'Ошибка обновления или удаления записей в таблице "%s" (%s)' % (table.name(), e))
                return errorMessageList, workLogMessageList

        
        for table, clientCol, description in tableListForDelete:
            step(u'Получение списка %s дубликата из таблицы %s' % (description, table.name()))
            existedIdList = db.getIdList(table, where = [table[clientCol].eq(duplicateClientId)])
            
            step(u'Удаление %d %s дубликата из таблицы %s' % (len(existedIdList), description, table.name()))
            db.transaction()
            try:
                db.deleteRecord(table, where = [table.idField().inlist(existedIdList)])
                db.commit()
                if existedIdList:
                    logOperation(u'В таблице "%s" удалены записи с id из списка %s' % (table.name(),
                                                                                       existedIdList))
            except Exception, e:
                db.rollback()
                errorMessageList.append(u'Ошибка удаления записей в таблице "%s" (%s)' % (table.name(), e))
                return errorMessageList, workLogMessageList
        
        step(u'Удаление дубликата с кодом %d из таблицы %s' % (duplicateClientId, tableClient.name()))
        db.transaction()
        try:
            db.deleteRecord(tableClient, where = [tableClient.idField().eq(duplicateClientId)])
            db.commit()
            logOperation(u'В таблице "%s" удалена запись с id = %s' % (tableClient.name(),
                                                                       duplicateClientId))
        except Exception, e:
            db.rollback()
            errorMessageList.append(u'Ошибка удаления записи в таблице "%s" (%s)' % (tableClient.name(), e))
        
        currentStep[0] = maxStep
        step(u'Объединение пациентов завершено')
                
        
        return errorMessageList, workLogMessageList
            
