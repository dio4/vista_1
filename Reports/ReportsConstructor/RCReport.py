# -*- coding: utf-8 -*-
import copy
import re
from PyQt4 import QtCore, QtGui

from Accounting.ContractComboBox import CContractComboBox
from Orgs.OrgComboBox import COrgComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportsConstructor.RCInfo import CRCQueryInfo
from Ui_ReportSetupDialog import Ui_RCReportDialog
from library.DateEdit import CDateEdit
from library.DbComboBox import CDbComboBox
from library.RBListBox import CRBListBox
from library.Utils import forceInt, forceString, forceDate, forceBool, forceDouble
from library.crbcombobox import CRBComboBox


class CRCQueryTable(object):
    counter = 0

    def __init__(self, parent, tableName, refField='', alias=''):
        self.parent = parent
        self.join = {}
        self.table = self.clearName(tableName)
        if alias:
            self.alias = alias
        else:
            self.createAlias(self.table)
        self.refField = refField
        self.tableFull = u'%s AS %s' % (self.table, self.alias)
        self.fields = []
        self.orders = []
        self.groups = []
        self.fieldsAlias = []
        self.conds = []
        self.increaseCounter()

    def __getitem__(self, item):
        return u'%s.`%s`' % (self.alias, item)

    def increaseCounter(self):
        self.__class__.counter += 1

    def getCounter(self):
        return self.__class__.counter

    def clearName(self, tableName):
        if re.search('^\(SELECT.*\)', tableName):
            return tableName
        return re.search('([\w.]+)(\[\d+\])?', tableName).groups()[0]

    def createAlias(self, tableName):
        self.alias = u'_'.join([tableName.replace('.', '_'), forceString(self.getCounter())])

    def appendCol(self, col, type='field'):
        if not col:
            return
        pattern, cols = col
        if forceString(pattern) == u'{0}':
            column = cols[0]
            fieldFull, alias, fieldWithAlias = self.append(column)
            if type == 'field':
                self.fields.append(fieldFull)
                self.fieldsAlias.append(alias)
            elif type == 'order':
                self.orders.append(fieldWithAlias)
            elif type == 'group':
                self.groups.append(fieldWithAlias)
            return fieldWithAlias
        else:
            columnList = []
            for column in cols:
                columnList.append(self.append(column))
            for idx, column in enumerate(columnList):
                fieldFull, alias, fieldWithAlias = column
                mask = '\{%d\}' % idx
                pattern = re.sub(mask, fieldWithAlias, pattern)
            if type == 'field':
                alias = 'additionalField_%d' % len(self.fieldsAlias)
                self.fields.append(('%s AS `%s`' % (pattern, alias)))
                self.fieldsAlias.append(alias)
            return forceString(pattern)

    def append(self, col):
        if isinstance(col, str) or isinstance(col, unicode):
            col = re.split('([ |])', col)
        if len(col) == 1:
            fieldName = col[0].split('.')[-1]
            if not fieldName:
                return None
            fieldAlias = u'_'.join([self.alias, fieldName])
            fieldWithAlias = u'%s.`%s`' % (self.alias, fieldName)
            fieldFull = u'%s AS %s' % (fieldWithAlias, fieldAlias)
            return fieldFull, fieldAlias, fieldWithAlias
        else:
            words = col[2].split('.')
            if len(words) == 3:
                refTable = u'.'.join(words[:2])
                refField = words[-1]
            else:
                refTable = words[0]
                refField = words[-1]
            field = col[0].split('.')[-1]
            joinType = col[1]
            type = 'inner'
            if joinType == u' ':
                type = 'inner'
            elif joinType == u'|':
                type = 'left'
            joinedTables = self.join.get(field, {})
            table, type = joinedTables.get(refTable, (CRCQueryTable(self, refTable, refField), type))
            self.join.setdefault(field, {})[refTable] = (table, type)
            return table.append(col[4:])

    def setTableLinks(self, tableLinks, subTables={}):
        if tableLinks:
            if tableLinks[0].get('field', None) == None:
                for link in tableLinks[1]:
                    self.setTableLinks(link, subTables)
                return
            link = tableLinks[0]
            joinedTables = self.join.get(link.get('field'), {})
            refTable = link.get('refTable', u'')
            refAlias = refTable if subTables.get(refTable) else u''
            refTable = subTables.get(refTable, refTable)
            table, type = joinedTables.get(refTable, (
            CRCQueryTable(self, refTable, link.get('refField', u''), alias=refAlias), link.get('type', 'inner')))
            self.join.setdefault(link.get('field', u''), {})[link.get('refTable', u'')] = (table, type)
            for link in tableLinks[1]:
                table.setTableLinks(link, subTables)
            return

    def setConditions(self, condTree, condDict):
        conds = self.appendConditions(condTree, condDict)
        self.conds = conds

    def appendConditions(self, condTree, condDict):
        db = QtGui.qApp.db
        condList = []
        for itemId, children in condTree.items():
            item = condDict.get(itemId)
            col, conditionTypeCode, valueType, value = item
            field = self.appendCol(col, type='cond')
            if valueType == 'field':
                value = self.appendCol(value, type='cond')
            if not (valueType == 'field' or conditionTypeCode == 'list' or valueType == 'list'):
                value = u"'%s'" % value
            if conditionTypeCode == 'and':
                condList.append(db.joinAnd(self.appendConditions(children, condDict)))
            elif conditionTypeCode == 'or':
                condList.append(db.joinOr(self.appendConditions(children, condDict)))
            elif valueType == 'list':
                condList.append(u"%s in %s" % (field, value))
            elif conditionTypeCode == 'eq':
                condList.append((u"%s = %s") % (field, value))
            elif conditionTypeCode == 'gt':
                condList.append((u"%s > %s") % (field, value))
            elif conditionTypeCode == 'ge':
                condList.append((u"%s >= %s") % (field, value))
            elif conditionTypeCode == 'lt':
                condList.append((u"%s < %s") % (field, value))
            elif conditionTypeCode == 'le':
                condList.append((u"%s <= %s") % (field, value))
            elif conditionTypeCode == 'list':
                condList.append(u"%s in %s" % (field, value))
            elif conditionTypeCode == 'ne':
                condList.append((u"%s <> %s") % (field, value))
            elif conditionTypeCode == 'true':
                condList.append((u"%s") % (field))
            elif conditionTypeCode == 'false':
                condList.append((u"not %s") % (field))
            elif conditionTypeCode == 'locate':
                condList.append((u"LOCATE(%s, %s)") % (value, field))
            elif valueType == 'custom':
                condList.append(field)
        return [cond for cond in condList if cond]

    def getQueryTable(self, queryTable=None):
        table = self
        result = []
        if not queryTable:
            queryTable = table
            result.append(queryTable.tableFull)
        for field, item in self.join.items():
            for refTableName, ref in item.items():
                ref, type = ref
                refTable = ref
                fieldWithoutFunc = re.search('\([0-9A-Za-z]+\)', field)
                if fieldWithoutFunc:
                    fieldWithoutFunc = fieldWithoutFunc.group()[1:-1]
                    fieldNew = re.sub('\([0-9A-Za-z]+\)', u'(%s)' % forceString(table[fieldWithoutFunc]), field)
                    cond = u'%s = %s' % (fieldNew, forceString(ref[ref.refField]))
                else:
                    cond = u'%s = %s' % (table[field], ref[ref.refField])
                join = u''
                if type == 'inner':
                    join = ' INNER JOIN %s ON %s '
                    # queryTable = queryTable.innerJoin(refTable, cond)
                elif type == 'left':
                    join = ' LEFT JOIN %s ON %s '
                    # queryTable = queryTable.leftJoin(refTable, cond)
                join = join % (refTable.tableFull, cond)
                result.append(join)
                result += (ref.getQueryTable(queryTable))
        return result

    def getQuery(self):
        table = self.getQueryTable()
        return table, self.fields, self.fieldsAlias, self.conds, self.groups, self.orders


class CRCReport(CReport):
    def __init__(self, parent, report):
        CReport.__init__(self, parent)
        self._report = report
        self._report._load()
        self.setTitle(report._name)
        self.modelCols = self._report.modelCols
        self.modelTableCap = self._report.modelTableCap
        self.modelTableCapGroup = self._report.modelTableCapGroup
        self.modelConditions = self._report.modelConditions
        self.modelParams = self._report.modelParams
        self.modelFunctions = self._report.modelFunctions
        self.modelGroups = self._report.modelGroups
        self.modelOrders = self._report.modelOrders
        self.queryCols = []

    def getSetupDialog(self, parent):
        result = CRCReportDialog(parent, self.modelParams)
        result.setTitle(self.title())
        return result

    def getTable(self, cursor):
        columnCount = self.modelTableCap._colsCount
        tableColumns = []
        tableCapItems = [item for idx, item in enumerate(self.modelTableCap.items())
                         if not self.modelTableCap.isGroupRow(idx) and not self.modelTableCap._fieldRow == idx]
        for column in range(columnCount):
            listTitle = []
            for rowItems in tableCapItems:
                title = ''
                item = rowItems.get(column, None)
                if item:
                    title = item.name()
                listTitle.append(title)
            tableColumns.append(
                ('%s%%' % forceString(forceDouble(100 / columnCount)), listTitle, CReportBase.AlignCenter))
        table = createTable(cursor, tableColumns)
        for row, rowItems in enumerate(self.modelTableCap.items()):
            for column, item in rowItems.items():
                if item.rowSpan() > 1 or item.columnSpan() > 1:
                    table.mergeCells(row, column, item.rowSpan(), item.columnSpan())
        return table, tableColumns

    def createQuery(self, params, query, subTables={}):
        modelFields = query.modelTree
        modelCols = query.modelCols
        modelConditions = query.modelConditions
        modelParams = query.modelParams
        modelParamsInfo = modelParams.getParams('id')
        modelFunctions = query.modelFunctions
        modelGroups = query.modelGroups
        modelOrders = query.modelOrders

        if hasattr(modelParams, 'translate'):
            translate = modelParams.translate

        def parceDateToString(date):
            if isinstance(date, QtCore.QDate):
                return forceString(date.toString('yyyy-MM-dd'))
            return forceString(date)

        def insertParamsToConds(conds):
            newConds = {}
            for id, cond in conds.items():
                field, additional = modelFields.parcePath(forceString(cond['field']))
                field = insertParams(field, True)
                field = insertFunctions(field)
                field = (field, additional)
                value = cond['value']
                conditionType = modelConditions._modelConditionType.getItem(cond['conditionType_id']).get('code', '')
                valueType = modelConditions._modelValueType.getItem(cond['valueType_id']).get('code', '')
                if valueType == 'param':
                    parametr = modelParamsInfo.get(value, {})
                    code = parametr.get('code')
                    if translate:
                        code = translate.get(code, code)
                    value = params.get(code, '')
                    if isinstance(value, dict):
                        value = [forceString(val) for val in value.keys()]
                    if isinstance(value, tuple):
                        value = [forceString(val) for val in value[1]]
                    valueType = modelConditions._modelValueType.getItem(parametr.get('valueType_id')).get('code', '')
                elif valueType == 'field':
                    value = modelFields.parcePath(value)
                elif valueType == 'custom':
                    field, additional = modelFields.parcePath(value)
                    field = insertParams(field, True)
                    field = insertFunctions(field)
                    field = (field, additional)
                if valueType == 'date':
                    value = parceDateToString(value)
                if valueType == 'list':
                    value = value if isinstance(value, list) else [value]
                    value = "(%s)" % u', '.join([u"'%s'" % forceString(val) for val in value])
                if not value:
                    value = '0'
                cond = (field, conditionType, valueType, value)
                newConds[id] = cond
            return newConds

        def insertParams(field, ignoreList=False):
            paramIds = re.findall('\{@[0-9]+\}', field)
            for paramId in paramIds:
                parametr = modelParamsInfo.get(paramId[2:-1], {})
                code = parametr.get('code')
                if translate:
                    code = translate.get(code, code)
                value = params.get(code, '')
                if parametr.get('type', u'') == 'date':
                    value = u"'%s'" % parceDateToString(value)
                if isinstance(value, dict):
                    value = [forceString(val) for val in value.keys()]
                if isinstance(value, tuple):
                    value = [forceString(val) for val in value[1]]
                if parametr.get('type', u'') in ['list', 'mixCmb', 'treeCmb']:
                    value = value if isinstance(value, list) else [value]
                    if ignoreList:
                        value = "('%s')" % u', '.join([forceString(val) for val in value])
                    else:
                        value = "(%s)" % u', '.join([u"'%s'" % forceString(val) for val in value])
                elif isinstance(value, list):
                    value = u"'%s'" % u' '.join([forceString(val) for val in value])
                if not value:
                    value = '0'
                field = field.replace(paramId, forceString(value))
            return field

        def insertFunctions(field):
            funcIds = re.findall('\{\$[0-9]+\}', field)
            for funcId in funcIds:
                function = modelFunctions.getItem(forceInt(funcId[2:-1]))
                value = function.get('function', u'')
                field = field.replace(funcId, value)
            return field

        def insertParamsInCols(cols):
            for idx, col in enumerate(cols):
                col, type = col
                field, additional = col
                field = insertParams(field)
                field = insertFunctions(field)
                cols[idx] = (field, additional), type
            return cols

        for stateId in query._stateTree.split(' '):
            for queryId in re.findall('q\d+', stateId):
                subQuery = CRCQueryInfo(self, modelParams, queryId[1:])
                subQuery._load()
                if not subTables.get(queryId):
                    stmt, queryCols, querySubTables = self.createQuery(params, subQuery, subTables=subTables)
                    subTables[queryId] = u'(%s)' % stmt
                    subTables.update(querySubTables)
                    for colRecord in subQuery.modelCols._items:
                        colId = u'f%s' % forceString(colRecord.value('id'))
                        colInfo = modelFields._items.get(colId, {})
                        if colInfo and colInfo.get('tableId', u'') == queryId:
                            modelFields._items[colId]['field'] = queryCols[forceInt(colRecord.value('number')) - 1]
                    queryItem = modelFields._items.get(queryId, {})
                    if queryItem:
                        modelFields._items[queryId]['field'] = modelFields._items.get(queryItem['field'], {}).get(
                            'field', queryItem['field'])

        table = CRCQueryTable(self, modelFields._rootItem._field)
        tableLinks = modelFields.getTableLinksFromState(query._stateTree)
        table.setTableLinks(tableLinks, subTables=subTables)

        cols = []
        modelsWithCols = [(modelCols, 'field')]
        if modelGroups:
            modelsWithCols.append(((modelGroups), 'group'))
        if modelOrders:
            modelsWithCols.append(((modelOrders), 'order'))
        for model, type in modelsWithCols:
            for item in model._items:
                cols.append((modelFields.parcePath(forceString(item.value('field'))), type))

        cols = insertParamsInCols(cols)
        condTree = modelConditions.getTreeId()
        condDict = insertParamsToConds(modelConditions._items)

        for col, type in cols:
            table.appendCol(col, type=type)
        table.setConditions(condTree, condDict)

        queryTable, queryCols, queryColsAlias, queryConds, queryGroups, queryOrders = table.getQuery()

        stmt = self.compileStmt(queryCols, queryTable, queryConds, queryGroups, queryOrders)
        return stmt, queryColsAlias, subTables

    def selectData(self, params):
        stmt, queryColsAlias, subTables = self.createQuery(params, self._report, subTables={})

        self.queryCols = queryColsAlias
        db = QtGui.qApp.db
        return db.query(stmt)

    def compileStmt(self, cols, tables, conds=[], groups=[], orders=[], limit=u''):
        stmt = []
        stmt.append('SELECT %s' % u', '.join(cols))
        stmt.append('FROM %s' % u' '.join(tables))
        if conds:
            stmt.append('WHERE %s' % u', '.join(conds))
        if groups:
            stmt.append('GROUP BY %s' % u', '.join(groups))
        if orders:
            stmt.append('ORDER BY %s' % u', '.join(orders))
        if limit:
            stmt.append('LIMIT %s' % limit)
        return u' '.join(stmt)

    def translateAlignment(self, value):
        result = CReportBase.AlignLeft
        if value == 0:
            result = CReportBase.AlignLeft
        elif value == 1:
            result = CReportBase.AlignCenter
        elif value == 2:
            result = CReportBase.AlignRight
        return result

    def translateCharFormat(self, value):
        if value:
            result = CReportBase.TableTotal
        else:
            result = CReportBase.TableBody
        return result

    def printGroups(self, table, data, groupId, groups):
        groupCount = 0
        if self.modelTableCap._groups.keys():
            groupCount = max(self.modelTableCap._groups.keys())
        if groupId > groupCount:
            for fields in data.get('items', []):
                self.printLine(table, fields)
        else:
            for key, item in data.items():
                if key in ['$fields', '$rows']:
                    continue
                groupData = item.get('$rows', {}).get('group', [])
                rows = {}
                for row, fields in enumerate(groupData):
                    rows[row] = self.printLine(table, fields, acceptEmpty=False)
                for row, fields in enumerate(groupData):
                    for column, field in enumerate(fields):
                        if field.get('rowSpan', 1) > 1 or field.get('columnSpan', 1) > 1:
                            table.mergeCells(rows[row], column, field.get('rowSpan', 1), field.get('columnSpan', 1))
                self.printGroups(table, item, groupId + 1, groups)
                groupData = item.get('$rows', {}).get('gtotal', [])
                rows = {}
                for fields in groupData:
                    self.printLine(table, fields, acceptEmpty=False)
                for row, fields in enumerate(groupData):
                    for column, field in enumerate(fields):
                        if field.get('rowSpan', 1) > 1 or field.get('columnSpan', 1) > 1:
                            table.mergeCells(rows[row], column, field.get('rowSpan', 1), field.get('columnSpan', 1))

    def printLine(self, table, fields, row=None, acceptEmpty=True):
        isEmpty = True
        if not acceptEmpty:
            for field in fields:
                if field.get('value', u''):
                    isEmpty = False
        if not acceptEmpty and isEmpty:
            return -1
        if not row:
            row = table.addRow()
        for col, val in enumerate(fields):
            table.setText(row, col, val.get('value', u''), self.translateCharFormat(val.get('format')),
                          self.translateAlignment(val.get('align')))
        return row

    def updateDictRecursive(self, data, insert):
        for key, item in insert.items():
            if isinstance(item, dict):
                result = self.updateDictRecursive(data.get(key, {}), item)
                data[key] = result
            elif isinstance(item, list):
                data[key] = data.get(key, []) + item
            else:
                data[key] = insert[key]
        return data

    def isGroupField(self, field):
        if re.search('\$count', field, re.IGNORECASE) or re.search('\$sum', field, re.IGNORECASE) or re.search(
                '\$multi', field, re.IGNORECASE):
            return True
        return False

    def countGroup(self, data, groupId, groups):
        if not groupId in groups.keys():
            return
        for itemKey, item in data.items():
            if itemKey in ['$fields', '$rows']:
                continue
            self.countGroup(item, groupId + 1, groups)
            groupingFields = item.get('$fields', {})
            for type in ['group', 'gtotal']:
                rows = groups.get(groupId, {}).get(type, {}).get('rows')
                if rows:
                    newRows = []
                    for row in rows:
                        newCols = []
                        for column in row:
                            field = column.get('field', u'')
                            if field:
                                column['value'] = self.countValues(field, groupingFields)
                            newCols.append(copy.deepcopy(column))
                        newRows.append(newCols)
                    data[itemKey].setdefault('$rows', {})[type] = newRows

    def countValues(self, expr, data):
        matchExpr = re.search('\$(\w+)\((\w+)\)', expr)
        matchLabel = re.search('\'(.+)\'', expr)
        matchField = re.search('^(\w+)', expr)
        if matchExpr:
            func = matchExpr.groups()[0].lower()
            field = matchExpr.groups()[1]
            values = data.get(field, [field])
            if func == 'sum':
                result = sum([self.forceNumber(val) for val in values])
                return result
            elif func == 'count':
                result = len([forceString(val) for val in values if val])
                return result
        elif matchLabel:
            return matchLabel.groups()[0]
        elif matchField:
            field = matchField.groups()[0]
            values = data.get(field, [field])
            return values[0]
        return u''

    def forceNumber(self, value):
        if re.search('^\d+\.\d+$', forceString(value)):
            return float('%.2f' % float(value))
        return forceInt(value)

    def getValue(self, record, field):
        type = QtCore.QVariant.typeToName(record.field(field).type())
        value = record.value(field)
        if type in ['QString']:
            return forceString(value)
        elif type in ['float', 'double']:
            return float('%.2f' % float(forceString(value)))
        elif type == 'int':
            return forceInt(value)
        elif type == 'QDate':
            # return forceDate(value).toString('dd:mm:yyyy')
            return forceString(value)
        return forceString(value)

    def getGroupingFieldsValues(self, record, group):
        result = {}
        for type in ['group', 'gtotal']:
            for field in group.get(type, {}).get('fields', []):
                result[field] = [forceString(record.value(field))]
        return result

    def dumpParams(self, cursor, params, charFormat=QtGui.QTextCharFormat()):
        result = []
        translate = {}
        if hasattr(self.modelParams, 'translate'):
            translate = self.modelParams.translate
        paramItems = self.modelParams.getParams()
        for code, item in paramItems.items():
            if item.get('type') == 'customCmb':
                result.append(u'%s: %s' % (
                item.get('title', u''), params.get(translate.get(code), {u'': u'не задано'}).values()[0]))
        text = u'\n'.join(result)
        if params.get('contractId'):
            params['contractIdList'] = params.get('contractId')[1]
            params['contractPath'] = params.get('contractId')[0]
        CReport.dumpParams(self, cursor, params, charFormat, additionalDescription=text)

    def build(self, params):
        query = self.selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        table, tableColumns = self.getTable(cursor)
        colsFormat = self.modelTableCap.items()[self.modelTableCap._fieldRow].items()
        cols = []
        for index, format in colsFormat:
            column = {}
            if format:
                column['align'] = format._alignment
                column['format'] = format._bold
            column['field'] = self.queryCols[format._value.get('number', index) - 1]
            cols.append(column)
        groups = {}
        for key, items in self.modelTableCap._groups.items():
            types = {}
            for item in items:
                rows = []
                type = {}
                type['fields'] = []
                for row in item[1]:
                    groupCols = []
                    for colIdx, col in self.modelTableCap._items[forceInt(row)].items():
                        column = {}
                        name = forceString(col._name)
                        for subStr in re.findall('\{f\d+\}', name):
                            name = name.replace(subStr, self.queryCols[forceInt(subStr[2:-1]) - 1])
                            type['fields'].append(self.queryCols[forceInt(subStr[2:-1]) - 1])
                        for subStr in re.findall('\{\$\w+\}', name):
                            name = name.replace(subStr,
                                                u"$%s" % self.modelFunctions._items.get(forceInt(subStr[2:-1]), {}).get(
                                                    'function', u''))

                        column['field'] = name
                        column['value'] = name
                        column['align'] = col._alignment
                        column['format'] = col._bold
                        column['rowSpan'] = col.rowSpan()
                        column['columnSpan'] = col.columnSpan()
                        groupCols.append(column)
                    rows.append(groupCols)
                type['rows'] = rows
                types[item[0]] = type
            groups[key] = types
        data = {}
        idx = 0
        while query.next():
            idx += 1
            currentData = {}
            record = query.record()
            fields = []
            for col in cols:
                col['value'] = self.getValue(record, col['field'])
                fields.append(col)
            currentData.setdefault('items', []).append(copy.deepcopy(fields))

            for groupId in sorted(groups.keys(), reverse=True):
                groupCol = self.queryCols[forceInt(self.modelTableCapGroup.getItem(groupId))] if len(
                    self.queryCols) > forceInt(self.modelTableCapGroup.getItem(groupId)) else '1'
                groupValue = forceString(record.value(groupCol))
                currentData['$fields'] = self.updateDictRecursive(currentData.get('$fields', {}),
                                                                  self.getGroupingFieldsValues(record,
                                                                                               groups.get(groupId)))
                currentData = {groupValue: currentData}

            data = self.updateDictRecursive(data, currentData)
        self.countGroup(data, 1, groups)
        self.printGroups(table, data, 1, groups)
        return doc


class CRCReportDialog(QtGui.QDialog, Ui_RCReportDialog):
    def __init__(self, parent=None, modelParams={}):
        QtGui.QDialog.__init__(self, parent)
        self.paramItems = modelParams.getParams()
        self.modelParams = modelParams
        self.inputs = {}
        self.inputs = self.setupUi(self, self.paramItems)
        self.initInputsData()
        self.initExtendedFunctions()

    def initExtendedFunctions(self):
        self.extendedFunction = {'orgStructureId': getOrgStructureDescendants}

    def initInputsData(self):
        for code, param in self.paramItems.items():
            for input in self.inputs.get(code, {}).values():
                if hasattr(input, 'setTable') and param.get('tableName', ''):
                    input.setTable(param.get('tableName', ''))
                if hasattr(input, 'setOrgId'):
                    input.setOrgId(QtGui.qApp.currentOrgId())
                    if hasattr(input, 'setValue'):
                        input.setValue(QtGui.qApp.currentOrgStructureId())
            if param.get('type', '') == 'customCmb':
                for input in self.inputs.get(code, {}).values():
                    if input.type == 'customCmb':
                        for value, title in param.get('values', []):
                            input.addItem(title)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        curDate = QtCore.QDate.currentDate()
        for inputs in self.inputs.values():
            for code, input in inputs.items():
                self.setInputValue(input, params.get(code))

    def params(self):
        result = {}
        translate = {}
        for paramCode in self.paramItems.keys():
            code, value = self.getParamValue(paramCode)
            if not value == None and not code == None:
                result[code] = value
                translate[paramCode] = code
        self.modelParams.translate = translate
        return result

    def setInputValue(self, input, value):
        if value == None:
            return
        if isinstance(input, (QtGui.QDateEdit, CDateEdit)):
            input.setDate(forceDate(value))
        elif isinstance(input, (CRBComboBox, COrgComboBox, COrgStructureComboBox, CDbComboBox)):
            input.setValue(value)
        elif isinstance(input, QtGui.QComboBox):
            if isinstance(value, dict):
                if len(value.keys()):
                    value = forceInt(value.keys()[0])
            if isinstance(value, int):
                input.setCurrentIndex(value)
        elif isinstance(input, QtGui.QCheckBox):
            input.setChecked(forceBool(value))

    def getInputValue(self, input):
        value = None
        if isinstance(input, (QtGui.QDateEdit, CDateEdit)):
            value = input.date()
        elif isinstance(input, (CRBComboBox, COrgComboBox, COrgStructureComboBox, CDbComboBox)):
            value = input.value()
        elif isinstance(input, CContractComboBox):
            value = (input.getPath(), input.getIdList())
        elif isinstance(input, QtGui.QComboBox):
            value = input.currentIndex()
        elif isinstance(input, QtGui.QCheckBox):
            value = input.isChecked()
        elif isinstance(input, CRBListBox):
            value = input.nameValues()
        value = self.getExtendedInputValue(input, value)
        return value

    def getParamValue(self, code):
        param = self.paramItems.get(code, {})
        inputs = self.inputs.get(code, {})
        if param:
            if param.get('type') == 'list':
                return self.getListParamValue(inputs)
            codeInput, input = self.inputs.get(code, {}).items()[0]
            return codeInput, self.getInputValue(input)
        return None, None

    def getListInputs(self, inputs):
        chk = None
        cmb = None
        lst = None
        for code, input in inputs.items():
            if input.type == 'chk':
                chk = input
            elif input.type == 'cmb':
                cmb = input
            elif input.type == 'lst':
                lst = input
        return chk, cmb, lst

    def getListParamValue(self, inputs):
        chk, cmb, lst = self.getListInputs(inputs)
        if not (chk and cmb and lst):
            return None, None
        if self.getInputValue(chk):
            return lst.code, self.getInputValue(lst)
        return cmb.code, self.getInputValue(cmb)

    def getExtendedInputValue(self, input, value):
        code = input.code
        type = input.type
        baseCode = input.baseCode
        function = self.extendedFunction.get(code, None)
        if function and value != None:
            value = function(value)
        if type == 'customCmb':
            valueList = self.paramItems.get(baseCode, {}).get('values', [])
            if valueList and value < len(valueList):
                value = {valueList[value][0]: valueList[value][1]}
        return value

    def listBehavior(self, bool):
        for inputs in self.inputs.values():
            chk, cmb, lst = self.getListInputs(inputs)
            if chk and cmb and lst:
                checked = chk.isChecked()
                cmb.setVisible(not checked)
                lst.setVisible(checked)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        if hasattr(self, 'cmbContract'):
            if hasattr(self.cmbContract, 'setBegDate'):
                self.cmbContract.setBegDate(date)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        if hasattr(self, 'cmbContract'):
            if hasattr(self.cmbContract, 'setEndDate'):
                self.cmbContract.setEndDate(date)

    @QtCore.pyqtSlot(int)
    def on_cmbFinance_currentIndexChanged(self, index):
        if hasattr(self, 'cmbContract') and hasattr(self, 'cmbFinance'):
            if hasattr(self.cmbContract, 'setFinanceId'):
                self.cmbContract.setFinanceId(self.cmbFinance.value())

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        for inputs in self.inputs.values():
            for input in inputs.values():
                if hasattr(input, 'setOrgStructureId'):
                    input.setOrgStructureId(orgStructureId)
