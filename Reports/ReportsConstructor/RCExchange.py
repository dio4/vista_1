# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015Vista Software. All rights reserved.
##
#############################################################################

import os
import zipfile
import re

from PyQt4 import QtCore, QtGui, QtXml
from library.Utils import forceStringEx, forceInt, forceDate, \
    forceBool, forceString, toVariant, getVal
from library.XML.XMLHelper import CXMLHelper

from Exchange.R85.ExchangeEngine import CExchangeEngine, CExchangeImportEngine

class CRCReportExportDialog(QtCore.QObject):
    def __init__(self, parent, idList):
        self._parent = parent
        self.idList = idList
        self._enging = CRCReportExport(self)

    def export(self):
        for reportId in self.idList:
            self._enging.process(reportId)
        self._enging.processRefBooks()

    def save(self):
        fileDir = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self._parent,
                                                                 u'Укажите директорию для сохранения файлов выгрузки',
                                                                       forceStringEx(getVal(
                                                    QtGui.qApp.preferences.appPrefs, 'ExportReportConstructor', ''))))
        if not fileDir:
            return
        nameParts = []
        if len(self.idList) == 1:
            nameParts.append(forceString(QtGui.qApp.db.translate('rcReport', 'id', self.idList[0], 'name')))
        else:
            nameParts.append(u'ReportExchange' )
        nameParts.append(forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh-mm')))
        name = u' '.join(nameParts)
        self._enging.save(fileDir, name)
        QtGui.QMessageBox.information(self._parent,
                                    u'Файл сохранен',
                                    u'Файл %s.zip сохранён.' % name,
                                     QtGui.QMessageBox.Ok,
                                     QtGui.QMessageBox.Ok)
        QtGui.qApp.preferences.appPrefs['ExportReportConstructor'] = toVariant(fileDir)

class CRCReportImportDialog(QtCore.QObject):
    def __init__(self, parent):
        self._parent = parent
        self._enging = CRCReportImport(self)

    def _import(self):
        fileDialog = QtGui.QFileDialog()
        fileName = fileDialog.getOpenFileName(
            self._parent, u'Укажите файлы с данными', forceStringEx(getVal(QtGui.qApp.preferences.appPrefs, 'ImportReportConstructor', '')), u'Файлы ZIP (*.zip)')
        if fileName:
            self._enging.openZip(fileName)
            self._enging.process()
            QtGui.QMessageBox.information(self._parent,
                                        u'Файл загружен',
                                        u'Файл %s загружен.' % fileName,
                                         QtGui.QMessageBox.Ok,
                                         QtGui.QMessageBox.Ok)
            QtGui.qApp.preferences.appPrefs['ImportReportConstructor'] = toVariant('/'.join(forceString(fileName).split('/')[:-1]))

class CRCReportExport(CExchangeEngine):
    version = u'2.1'

    def __init__(self, parent):
        CExchangeEngine.__init__(self)
        self._parent = parent
        self.documents = {}

    def getValue(self, record, field):
        type = QtCore.QVariant.typeToName(record.field(field).type())
        value = record.value(field)
        if type in ['QString', 'float']:
            return forceString(value)
        if type == 'int':
            return forceInt(value)
        elif type == 'QDate':
            return forceDate(value).toString('dd:mm:yyyy')

    def addHeaderElement(self, rootElement):
        header = CXMLHelper.addElement(rootElement, 'HEADER')
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'VERSION'),   # Версия взаимодействия
                            self.version[:5])
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'DATA'),      # Дата
                            QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate))
        return header

    def setRecordValuesToElement(self, element, record, fields):
        for field in fields:
            CXMLHelper.setValue(CXMLHelper.addElement(element, forceStringEx(field).upper()),
                            self.getValue(record, field))

    def addReportElement(self, rootElement, record):
        report = CXMLHelper.addElement(rootElement, 'REPORT')
        self.setRecordValuesToElement(report, record, ['name', 'description', 'editionMode', 'sql'])
        db = QtGui.qApp.db

        queryRecord = db.getRecord(db.table('rcQuery'), '*', forceInt(record.value('query_id')))
        if queryRecord:
            self.addQueryElement(report, queryRecord)

        params = CXMLHelper.addElement(report, 'PARAMETRS')
        for paramRecord in self.getReportParameterRecords(record.value('id')):
            self.addReportParamElement(params, paramRecord)

        groups = CXMLHelper.addElement(report, 'GROUPS')
        for groupRecord in db.getRecordList('rcReport_Group', '*', 'master_id = %d and deleted = 0' % forceInt(record.value('id')), 'number'):
            self.addReportGroupElement(groups, groupRecord)

        capCells = CXMLHelper.addElement(report, 'TABLECAPCELLS')
        for tableCapCellRecord in db.getRecordList('rcReport_TableCapCells', '*', 'master_id = %d' % forceInt(record.value('id'))):
            self.addCapCellElement(capCells, tableCapCellRecord)


        return report

    def addQueryElement(self, parentElement, record):
        query = CXMLHelper.addElement(parentElement, 'QUERY')
        self.setRecordValuesToElement(query, record, ['id', 'name', 'stateTree', 'referencedField', 'mainTable_id'])
        db = QtGui.qApp.db

        columns = CXMLHelper.addElement(query, 'COLUMNS')
        for columnRecord in db.getRecordList('rcQuery_Cols', '*', 'master_id = %d and deleted = 0' % forceInt(record.value('id')), 'number'):
            self.addColumnElement(columns, columnRecord)

        orders = CXMLHelper.addElement(query, 'ORDERS')
        for orderRecord in db.getRecordList('rcQuery_Order', '*', 'master_id = %d and deleted = 0' % forceInt(record.value('id')), 'number'):
            self.addOrderElement(orders, orderRecord)

        groups = CXMLHelper.addElement(query, 'GROUPS')
        for groupRecord in db.getRecordList('rcQuery_Group', '*', 'master_id = %d and deleted = 0' % forceInt(record.value('id')), 'number'):
            self.addGroupElement(groups, groupRecord)

        conds = CXMLHelper.addElement(query, 'CONDITIONS')
        for headConditionRecord in self.getConditionRecords(record.value('id')):
            self.addConditionElement(conds, headConditionRecord)

        subQuerys = CXMLHelper.addElement(query, 'QUERYES')
        subQueryIdList = [u"'%s'" % forceString(subQueryId) for subQueryId in re.findall('q(\d+)', forceString(record.value('stateTree')))]
        if subQueryIdList:
            for queryRecord in db.getRecordList('rcQuery', '*', 'id in (%s)' % u', '.join(subQueryIdList)):
                self.addQueryElement(subQuerys, queryRecord)

        return query

    def addColumnElement(self, parentElement, record):
        column = CXMLHelper.addElement(parentElement, 'COLUMN')
        self.setRecordValuesToElement(column, record, ['id', 'number', 'field', 'visible', 'extended', 'alias'])
        return column

    def addOrderElement(self, parentElement, record):
        order = CXMLHelper.addElement(parentElement, 'ORDER')
        self.setRecordValuesToElement(order, record, ['number', 'field', 'visible', 'extended', 'alias'])
        return order

    def addGroupElement(self, parentElement, record):
        group = CXMLHelper.addElement(parentElement, 'GROUP')
        self.setRecordValuesToElement(group, record, ['number', 'field', 'visible', 'extended', 'alias'])
        return group

    def addConditionElement(self, parentElement, record):
        condition = CXMLHelper.addElement(parentElement, 'CONDITION')
        self.setRecordValuesToElement(condition, record, ['field', 'value', 'conditionType_id', 'valueType_id'])

        subConditions = CXMLHelper.addElement(condition, 'CONDITIONS')
        for conditionRecord in self.getConditionRecords(record.value('master_id'), record.value('id')):
            self.addConditionElement(subConditions, conditionRecord)
        return condition

    def addReportParamElement(self, parentElement, record):
        param = CXMLHelper.addElement(parentElement, 'PARAMETR')
        self.setRecordValuesToElement(param, record, ['param_id'])
        return param

    def addReportGroupElement(self, parentElement, record):
        group = CXMLHelper.addElement(parentElement, 'GROUP')
        self.setRecordValuesToElement(group, record, ['number', 'field'])
        return group

    def addCapCellElement(self, parentElement, record):
        capCell = CXMLHelper.addElement(parentElement, 'CAPCELL')
        self.setRecordValuesToElement(capCell, record, ['name', 'row', 'column', 'rowSpan', 'columnSpan', 'alignment', 'type', 'bold'])
        return capCell

    def addRbElement(self, parentElement, rbName):
        rb = CXMLHelper.addElement(parentElement, 'REFBOOK')
        CXMLHelper.setValue(CXMLHelper.addElement(rb, 'NAME'),
                            rbName)
        db = QtGui.qApp.db

        if rbName == 'rcField':
            for record in db.getRecordList('rcField', '*', 'deleted = 0'):
                self.addFieldElement(rb, record)
        elif rbName == 'rcFunction':
            for record in db.getRecordList('rcFunction', '*'):
                self.addFunctionElement(rb, record)
        elif rbName == 'rcConditionType':
            for record in db.getRecordList('rcConditionType', '*', 'deleted = 0'):
                self.addConditionTypeElement(rb, record)
        elif rbName == 'rcValueType':
            for record in db.getRecordList('rcValueType', '*'):
                self.addValueTypeElement(rb, record)
        elif rbName == 'rcTable':
            for record in db.getRecordList('rcTable', '*', 'deleted = 0'):
                self.addTableElement(rb, record)
        elif rbName == 'rcParamType':
            for record in db.getRecordList('rcParamType', '*'):
                self.addParamTypeElement(rb, record)
        elif rbName == 'rcParam':
            for record in db.getRecordList('rcParam', '*'):
                self.addParamElement(rb, record)
        elif rbName == 'rcParamValues':
            for record in db.getRecordList('rcParam_Value', '*'):
                self.addParamValueElement(rb, record)
        return rb

    def addFieldElement(self, parentElement, record):
        field = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(field, record, ['id', 'name', 'field', 'ref_id', 'rcTable_id', 'description', 'visible'])
        return field

    def addFunctionElement(self, parentElement, record):
        function = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(function, record, ['id', 'name', 'function', 'description'])
        return function

    def addConditionTypeElement(self, parentElement, record):
        conditionType = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(conditionType, record, ['id', 'name', 'sign', 'code'])
        return conditionType

    def addValueTypeElement(self, parentElement, record):
        valueType = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(valueType, record, ['id', 'name', 'code'])
        return valueType

    def addTableElement(self, parentElement, record):
        table = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(table, record, ['id', 'name', 'table', 'description', 'visible', 'group'])
        return table

    def addParamTypeElement(self, parentElement, record):
        paramType = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(paramType, record, ['id', 'name', 'code'])
        return paramType

    def addParamElement(self, parentElement, record):
        param = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(param, record, ['id', 'name', 'code', 'title', 'tableName', 'valueType_id', 'type_id'])
        db = QtGui.qApp.db
        return param

    def addParamValueElement(self, parentElement, record):
        param = CXMLHelper.addElement(parentElement, 'RECORD')
        self.setRecordValuesToElement(param, record, ['id', 'value', 'title', 'master_id', 'number'])

    def createXMLDocument(self, title):
        doc = CXMLHelper.createDomDocument(rootElementName='MAIN', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        self.addHeaderElement(rootElement)
        return doc, rootElement

    def process(self, reportId):
        db = QtGui.qApp.db
        reportRecord = db.getRecord('rcReport', '*', reportId)
        if reportRecord:
            reportName = forceString(reportRecord.value('name'))
            doc, rootElement = self.createXMLDocument(reportName)
            self.addReportElement(rootElement, reportRecord)
            self.documents[reportName] = doc

    def processRefBooks(self):
        rbNameList = ['rcField', 'rcFunction', 'rcConditionType', 'rcValueType', 'rcTable', 'rcParamType', 'rcParam', 'rcParamValues']
        for rbName in rbNameList:
            doc, rootElement = self.createXMLDocument(rbName)
            rb = self.addRbElement(rootElement, rbName)
            self.documents[rbName] = doc

    def getRecords(self, stmt):
        db = QtGui.qApp.db
        records = []
        query = db.query(stmt)
        while query.next():
            records.append(query.record())
        return records

    def getConditionRecords(self, queryId, parentId=None):
        stmt = u"""
            Select
                cond.id,
                cond.field,
                cond.value,
                cond.conditionType_id,
                cond.valueType_id,
                cond.master_id,
                cond.parentCondition_id
            From rcQuery_Conditions cond
            Where cond.master_id = %s
                and cond.parentCondition_id %s
        """ % (forceString(queryId),
              u'= %s' %forceString(parentId) if parentId else u'is NULL')
        return self.getRecords(stmt)

    def getReportParameterRecords(self, reportId):
        stmt = u"""
            Select reportParams.param_id
            From rcReport_Params reportParams
            Where reportParams.master_id = %s
        """ % forceString(reportId)
        return self.getRecords(stmt)

    def save(self, outDir, zipName):
        outDir = forceStringEx(outDir)
        try:
            zipFilePath = forceStringEx(unicode(os.path.join(outDir, u'%s.zip' % zipName)))
            zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
            for reportName in self.documents.keys():
                doc = self.documents[reportName]
                fileName = u''.join([reportName])
                xmlFileName = QtCore.QTemporaryFile(u'%s.xml' % fileName)
                if not xmlFileName.open(QtCore.QFile.WriteOnly):
                    print u'Не удалось открыть временный файл для записи'
                    break
                doc.save(QtCore.QTextStream(xmlFileName), 4, QtXml.QDomNode.EncodingFromDocument)
                xmlFileName.close()
                zf.write(forceStringEx(QtCore.QFileInfo(xmlFileName).absoluteFilePath()), u'%s.xml' % fileName)
                self.documents.pop(reportName)
            zf.close()
        except Exception, e:
            pass

class CRCReportImport(CExchangeImportEngine):
    def __init__(self, parent):
        CExchangeImportEngine.__init__(self)
        self._parent = parent
        self.documents = {}

    def openZip(self, zipFileName):
        if not zipfile.is_zipfile(forceString(zipFileName)):
            QtGui.qApp.processEvents()
            return False

        archive = zipfile.ZipFile(forceString(zipFileName), "r")
        names = archive.namelist()
        for fileName in names:
            docFile = archive.read(fileName)
            self.documents[fileName] = CXMLHelper.loadDocument(docFile)

    def process(self):
        doc = self.documents.pop('rcTable.xml')
        self.translateTables = {}
        self.translateFields = {}
        self.translateParams = {}
        self.translateParamValues = {}
        self.translateParamTypes = {}
        self.translateValueTypes = {}
        self.translateSubQuerys = {}
        self.translateQueryCols = {}
        if doc:
            newTables = self.parceRefBook(doc, ['id', 'name', 'table', 'description', 'visible', 'group'])
            newTables = self.updateTableNames(newTables)
            currentTables = self.loadRefBook('rcTable', ['name', 'table', 'description', 'visible', 'group'])
            self.translateTables = self.compareAndUpdateRefBook(newTables, currentTables, 'rcTable', ['table'])
        doc = self.documents.pop('rcField.xml')
        if doc:
            newFields = self.parceRefBook(doc, ['id', 'name', 'field', 'ref_id', 'rcTable_id', 'description', 'visible'])
            self.translateItems(newFields, 'rcTable_id', self.translateTables)
            currentFields = self.loadRefBook('rcField', ['name', 'field', 'ref_id', 'rcTable_id', 'description', 'visible'])
            self.translateFields = self.compareFields(newFields, currentFields, 'rcField', ['name', 'field', 'rcTable_id'], ['ref_id'])
        doc = self.documents.pop('rcValueType.xml')
        if doc:
            newValueTypes = self.parceRefBook(doc, ['id', 'name', 'code'])
            currentValueTypes = self.loadRefBook('rcValueType', ['name', 'code'])
            self.translateValueTypes = self.compareAndUpdateRefBook(newValueTypes, currentValueTypes, 'rcValueType', ['code'])
        doc = self.documents.pop('rcParamType.xml')
        if doc:
            newParamTypes = self.parceRefBook(doc, ['id', 'name', 'code'])
            currentParamTypes = self.loadRefBook('rcParamType', ['name', 'code'])
            self.translateParamTypes = self.compareAndUpdateRefBook(newParamTypes, currentParamTypes, 'rcParamType', ['code'])
        doc = self.documents.pop('rcParam.xml')
        if doc:
            newParams = self.parceRefBook(doc, ['id', 'name', 'code', 'title', 'tableName', 'valueType_id', 'type_id'])
            self.translateItems(newParams, 'valueType_id', self.translateValueTypes)
            self.translateItems(newParams, 'type_id', self.translateParamTypes)
            currentParams = self.loadRefBook('rcParam', ['name', 'code', 'title', 'tableName', 'valueType_id', 'type_id'])
            self.translateParams = self.compareAndUpdateRefBook(newParams, currentParams, 'rcParam', ['code'])
        doc = self.documents.pop('rcParamValues.xml')
        if doc:
            newParamValues = self.parceRefBook(doc, ['id', 'title', 'value', 'master_id', 'number'])
            self.translateItems(newParamValues, 'master_id', self.translateParams)
            currentParamValues = self.loadRefBook('rcParam_Value', ['title', 'value', 'master_id', 'number'])
            self.translateParamValues = self.compareAndUpdateRefBook(newParamValues, currentParamValues, 'rcParam_Value', ['master_id', 'number'])
        doc = self.documents.pop('rcFunction.xml')
        if doc:
            newFunctions = self.parceRefBook(doc, ['id', 'name', 'function', 'description', 'hasSpace'])
            currentFunctions = self.loadRefBook('rcFunction', ['name', 'function', 'description', 'hasSpace'])
            self.translateFunctions = self.compareAndUpdateRefBook(newFunctions, currentFunctions, 'rcFunction', ['function'])
        doc = self.documents.pop('rcConditionType.xml')
        if doc:
            newConditionTypes = self.parceRefBook(doc, ['id', 'name', 'sign', 'code'])
            currentConditionTypes = self.loadRefBook('rcConditionType', ['name', 'sign', 'code'])
            self.translateConditionTypes = self.compareAndUpdateRefBook(newConditionTypes, currentConditionTypes, 'rcConditionType', ['code'])

        for docReport in self.documents.values():
            self.processReport(docReport)

    def processReport(self, doc):
        db = QtGui.qApp.db
        rootElement = CXMLHelper.getRootElement(doc)
        reportElement = self.getElement(rootElement, 'REPORT', True)
        reportName = self.getElementValue(reportElement, 'NAME')
        reportId = db.translate('rcReport', 'name', reportName, 'id')
        if reportId:
            msg = QtGui.QMessageBox.warning(self._parent._parent,
                                    u'Внимание!',
                                    u"Отчёт с именем '%s' уже существует.\nOk - заменить.\nSave - сохранить с другим именем." % reportName,
                                     QtGui.QMessageBox.Ok | QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel,
                                     QtGui.QMessageBox.Ok)
            if msg == QtGui.QMessageBox.Cancel:
                return
            elif msg == QtGui.QMessageBox.Ok:
                self.deleteReport(reportId)
            elif msg == QtGui.QMessageBox.Save:
                idx = 1
                while db.translate('rcReport', 'name', u'%s_%d' % (reportName, idx), 'id'):
                    idx += 1
                reportName = u'%s_%d' % (reportName, idx)
        self.parceReport(reportElement, reportName)

    def parceReport(self, reportElement, reportName):
        report = self.getElementItemValue(reportElement, list=['name', 'description', 'editionMode', 'sql'])
        report['name'] = reportName
        queryElement = self.getElement(reportElement, 'QUERY')
        report['query_id'] = self.parceQuery(queryElement).values()[0]
        report['id'] = self.insertIntoTable('rcReport', report)

        parametrsElement = self.getElement(reportElement, 'PARAMETRS')
        for parametrElement in self.getElementList(parametrsElement, 'PARAMETR'):
            param = self.getElementItemValue(parametrElement, list=['param_id'])
            param['param_id'] = self.translateParams.get(param['param_id'], param['param_id'])
            param['master_id'] = report['id']
            self.insertIntoTable('rcReport_Params', param)

        tableCapCellsElement = self.getElement(reportElement, 'TABLECAPCELLS')
        for capCellElement in self.getElementList(tableCapCellsElement, 'CAPCELL'):
            capCell = self.getElementItemValue(capCellElement, list=['name', 'row', 'column', 'rowSpan', 'columnSpan', 'alignment', 'type', 'bold'])
            capCell['master_id'] = report['id']
            self.insertIntoTable('rcReport_TableCapCells', capCell)

        reportGroupsElement = self.getElement(reportElement, 'GROUPS')
        for reportGroupElement in self.getElementList(reportGroupsElement, 'GROUP'):
            reportGroup = self.getElementItemValue(reportGroupElement, list=['number', 'field'])
            reportGroup['master_id'] = report['id']
            self.insertIntoTable('rcReport_Group', reportGroup)

    def parceQuery(self, queryElement):
        query = self.getElementItemValue(queryElement, list=['name', 'stateTree', 'mainTable_id'])
        query['oldId'] = self.getElementValue(queryElement, 'ID')
        query['mainTable_id'] = self.translateTables.get(query['mainTable_id'], query['mainTable_id'])

        subQuerysElement = self.getElement(queryElement, 'QUERYES')
        for subQueryElement in self.getElementList(subQuerysElement, 'QUERY'):
            self.translateSubQuerys.update(self.parceQuery(subQueryElement))

        query['stateTree'] = self.translateState(query['stateTree'])
        query['referencedField'] = self.getElementValue(queryElement, 'REFERENCEDFIELD')
        query['referencedField'] = self.translateField(query['referencedField'])
        query['id'] = self.insertIntoTable('rcQuery', query)

        columnsElement = self.getElement(queryElement, 'COLUMNS')
        for columnElement in self.getElementList(columnsElement, 'COLUMN'):
            column = self.getElementItemValue(columnElement, list=['id', 'number', 'field', 'visible', 'extended', 'alias'])
            column['field'] = self.translateField(column['field'])
            column['master_id'] = query['id']
            self.translateQueryCols.update({column['id']: self.insertIntoTable('rcQuery_Cols', column)})

        ordersElement = self.getElement(queryElement, 'ORDERS')
        for orderElement in self.getElementList(ordersElement, 'ORDER'):
            order = self.getElementItemValue(orderElement, list=['number', 'field', 'visible', 'extended', 'alias'])
            order['field'] = self.translateField(order['field'])
            order['master_id'] = query['id']
            self.insertIntoTable('rcQuery_Order', order)

        groupsElement = self.getElement(queryElement, 'GROUPS')
        for groupElement in self.getElementList(groupsElement, 'GROUP'):
            group = self.getElementItemValue(groupElement, list=['number', 'field', 'visible', 'extended', 'alias'])
            group['field'] = self.translateField(group['field'])
            group['master_id'] = query['id']
            self.insertIntoTable('rcQuery_Group', group)

        conditionsElement = self.getElement(queryElement, 'CONDITIONS')
        self.parceConditions(conditionsElement, query['id'])
        return {query['oldId']: query['id']}

    def parceConditions(self, conditionsElement, master_id, parent_id=None):
        for conditionElement in self.getElementList(conditionsElement, 'CONDITION'):
            condition = self.getElementItemValue(conditionElement, list=['field', 'value', 'conditionType_id', 'valueType_id'])
            condition['conditionType_id'] = self.translateConditionTypes.get(condition['conditionType_id'], condition['conditionType_id'])
            condition['valueType_id'] = self.translateValueTypes.get(condition['valueType_id'], condition['valueType_id'])
            condition['master_id'] = master_id
            condition['field'] = self.translateField(condition['field'])
            condition['value'] = self.translateField(condition['value'], condition['valueType_id'])
            condition['parentCondition_id'] = parent_id
            condition['id'] = self.insertIntoTable('rcQuery_Conditions', condition)
            subConditionsElement = self.getElement(conditionElement, 'CONDITIONS')
            self.parceConditions(subConditionsElement, master_id, condition['id'])


    def translateState(self, state):
        patternField = re.compile('[il]\d+')
        patternSubQuery = re.compile('q\d+')
        translate = {}
        for index, id in enumerate(re.findall(patternField, state), len(translate.keys())):
            preId = id[0]
            key = u'[%d]' % index
            translate[key] = forceString(self.translateFields.get(id[1:], id[1:]))
            state = state.replace(id, u''.join([preId, key]))

        for index, id in enumerate(re.findall(patternSubQuery, state), len(translate.keys())):
            key = u'[%d]' % index
            translate[key] = forceString(self.translateSubQuerys.get(id[1:], id[1:]))
            state = state.replace(id, u'q%s' % key)

        for key, value in translate.items():
            state = state.replace(key, value)
        return state

    def translateField(self, field, valueTypeId=None):
        valueTypeCode = forceString(QtGui.qApp.db.translate('rcValueType', 'id', valueTypeId, 'code')) if valueTypeId else u''
        if valueTypeCode == 'param':
            return self.translateParams.get(field, field)
        elif valueTypeCode == 'field':
            return self.translateText(field, field=True)
        elif valueTypeCode == 'custom':
            return self.translateText(field, True, True, True, True)
        elif not valueTypeCode:
            return self.translateText(field, True, True, True, True)
        return field

    def translateText(self, text, field=False, func=False, param=False, query=False):
        patternSubQuery = re.compile('q\d+')
        patternSubQueryCol = re.compile('f\d+')
        patternParam = re.compile('@\d+')
        patternFunc = re.compile('\$\d+')
        result = []
        for word in re.split('([\{\}])', text):
            ids = re.split('([\.|])', word)
            for index, id in enumerate(ids):
                if id in [u'.', u'|']:
                    continue
                if re.search(patternFunc, id) and func:
                    ids[index] = u'$%s' % self.translateFunctions.get(id[1:], id[1:])
                elif re.search(patternParam, id) and param:
                    ids[index] = u'@%s' % self.translateParams.get(id[1:], id[1:])
                elif re.search(patternSubQuery, id) and query:
                    ids[index] = u'q%s' % self.translateSubQuerys.get(id[1:], id[1:])
                elif re.search(patternSubQueryCol, id) and query:
                    ids[index] = u'f%s' % self.translateQueryCols.get(id[1:], id[1:])
                elif field:
                    ids[index] = self.translateFields.get(id, id)
            result.append(u''.join(ids))
        return u''.join(result)

    def translateItems(self, items, field, translate):
        for item in items.values():
            item[field] = translate.get(item.get(field), item.get(field))

    def updateTable(self, tableName, items):
        translate = {}
        for item in items:
            newId = self.insertIntoTable(tableName, item)
            id = item.get('id')
            translate[forceString(id)] = forceString(newId)
        return translate

    def insertIntoTable(self, tableName, item):
        db = QtGui.qApp.db
        table = db.table(tableName)
        record = table.newRecord()
        for field, value in item.items():
            type = QtCore.QVariant.typeToName(record.field(field).type())
            if not field in ['id', 'ref_id'] and forceBool(forceString(value)):
                if type == 'int':
                    if forceInt(value):
                        record.setValue(field, toVariant(value))
                else:
                    record.setValue(field, toVariant(value))
        newId = db.insertRecord(table, record)
        return newId

    def parceRefBook(self, doc, fieldList):
        result = {}
        for recordElement in self.getRBRecordElementList(doc):
            result.update(self.getElementItemValue(recordElement, 'id', fieldList))
        return result

    def loadRefBook(self, tableName, fieldList):
        db = QtGui.qApp.db
        result = {}
        for record in db.getRecordList(tableName, '*'):
            item = {}
            for valueName in fieldList:
                item[valueName] = forceString(record.value(valueName))
            result[forceString(record.value('id'))] = item
        return result

    def compareFields(self, newFields, currentFields, tableName, fieldListToCompare, notRequiredFieldList):
        translate, difference, update = self.compareRefBooksEx(newFields, currentFields, fieldListToCompare, notRequiredFieldList)
        translate.update(self.updateTable(tableName, difference))

        for item in difference + update:
            ref_id = translate.get(item['ref_id'], item['ref_id'])
            if forceInt(ref_id):
                ref_id = u"'%s'" % ref_id
            else:
                ref_id = u'NULL'
            stmt = """Update rcField set `ref_id` = %s where `id` = '%s' and (not `ref_id` or isNull(`ref_id`))""" %(ref_id, translate.get(item['id'], item['id']))
            QtGui.qApp.db.query(stmt)


        for item in update:
            updateFieldList = []
            for field in notRequiredFieldList:
                if field == 'ref_id' and forceInt(item.get(field)):
                    updateFieldList.append(u"`%s` = '%s'" % (field, translate.get(item['ref_id'], item['ref_id'])))
                elif item.get(field) != None and field not in ['ref_id']:
                    updateFieldList.append(u"`%s` = '%s'" % (field, item.get(field)))
            if updateFieldList:
                stmt = u"Update %s set %s where `id` = '%s'" %(tableName, u', '.join(updateFieldList), translate.get(item['id'], item['id']))
                QtGui.qApp.db.query(stmt)
        return translate

    def compareAndUpdateRefBook(self, newRb, currentRb, tableName, fieldListToCompare):
        translate, difference = self.compareRefBooks(newRb, currentRb, fieldListToCompare)
        translate.update(self.updateTable(tableName, difference))
        return translate

    def compareRefBooks(self, newRB, currentRB, fieldList):
        translate = {}
        difference = []
        for newId, newItem in newRB.items():
            found = False
            for curId, currentItem in currentRB.items():
                if self.compareItems(newItem, currentItem, fieldList):
                    found = True
                    if curId != newId:
                        translate[forceString(newId)] = forceString(curId)
                        break
            if not found:
                difference.append(newItem)
        return translate, difference

    def compareRefBooksEx(self, newRB, currentRB, fieldList, notRequiredFieldList):
        translate = {}
        difference = []
        update = []
        for newId, newItem in newRB.items():
            found = False
            for curId, currentItem in currentRB.items():
                if self.compareItems(newItem, currentItem, fieldList):
                    found = True
                    if curId != newId:
                        translate[forceString(newId)] = forceString(curId)
                    break
            if not found:
                difference.append(newItem)
            else:
                if not self.compareItems(newItem, currentItem, notRequiredFieldList):
                   update.append(newItem)
        return translate, difference, update

    def compareItems(self, newItem, curItem, fieldList):
        result = True
        for field in fieldList:
            if forceString(newItem.get(field, 0)).lower().strip() != forceString(curItem.get(field, 1)).lower().strip():
                result = False
        return result

    def getElementItemValue(self, element, key=None, list=[], hasValues=False):
        if key != None:
            keyValue = self.getElementValue(element, key.upper())
        result = {}
        for valueName in list:
            result[valueName] = self.getElementValue(element, valueName.upper())
        if key != None:
            return {keyValue: result}
        return result

    def getRBRecordElementList(self, doc):
        rootElement = CXMLHelper.getRootElement(doc)
        rbElement = self.getElement(rootElement, 'REFBOOK', True)
        return self.getElementList(rbElement, 'RECORD')

    def getElementList(self, parentElement, elementName):
        list = []
        recordElement = parentElement.firstChildElement(elementName)
        while recordElement.hasChildNodes():
            list.append(recordElement)
            recordElement = recordElement.nextSiblingElement(elementName)
        return list

    def getElementValue(self, parentNode, elementName):
        return forceString(self.getElement(parentNode, elementName).text())

    def deleteReport(self, reportId):
        db = QtGui.qApp.db
        db.deleteRecord('rcReport', "id = '%s'" % forceString(reportId))

    def updateTableNames(self, tables):
        from Reports.ReportsConstructor.RCFieldList import CRCInitFields
        initFields = CRCInitFields(self)
        initFields.getAllTablesFromDb()
        result = {}
        for id, tableInfo in tables.items():
            tables[id]['table'] = initFields.checkTableExists(tableInfo['table'])
        return tables