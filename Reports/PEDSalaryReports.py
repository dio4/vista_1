# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from copy import copy
from types import DictType

from Orgs.Utils import getOrgStructureDescendants, getOrgStructureName
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_PEDSalaryReportsSetup import Ui_PEDSalaryReportsSetupDialog
from library.Utils import forceDouble, forceInt, forceRef, forceString


def getActionTypeName(id):
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    record = db.getRecordEx(tableActionType, [tableActionType['name']], [tableActionType['id'].eq(id)])
    name = None
    if record:
        name = forceString(record.value('name'))
    return name


def getPersonFIO(id):
    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    cols = [tablePerson['lastName'], tablePerson['firstName'], tablePerson['patrName']]
    record = db.getRecordEx(tablePerson, cols, [tablePerson['id'].eq(id)])
    name = None
    if record:
        name = "%s %s %s" % (forceString(record.value('lastName')),
                             forceString(record.value('firstName')),
                             forceString(record.value('patrName')),)
    return name


def getShortFIO(lastName, firstName, patrName):
    return "%s %s%s" % (lastName,
                        firstName and "%s." % firstName[0] or "",
                        patrName and "%s." % patrName[0] or "")


def getPayStatusInt(payStatus, financeCode):
    return (payStatus & ((2 ** (financeCode * 2)) * 3)) >> financeCode * 2


class CPEDSalaryReports(CReport):
    basename = u'Отчет по заработной плате'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.basename, 'PEDSalaryReports')

    def getSetupDialog(self, parent):
        result = CPEDSalaryReportsSetupDialog(parent)
        return result

    def getDescription(self, params):
        typeRepN = params['typeRep'][0]
        begDate = params.get('begDate', QtCore.QDate.currentDate())
        endDate = params.get('endDate', QtCore.QDate.currentDate())
        ServiceId = params.get('ServiceId', None)
        byPerformer = params.get('byPerformer', True)
        PerformerId = params.get('PerformerId', None)
        AssistantId = params.get('AssistantId', None)
        AssistantId2 = params.get('AssistantId2', None)
        AssistantId3 = params.get('AssistantId3', None)
        OrgStrId = params.get('OrgStrId', None)
        ClientId = params.get('ClientId', None)
        lastName = params.get('lastName', '')
        firstName = params.get('firstName', '')
        patrName = params.get('patrName', '')
        byCode = params.get('byCode', True)
        rows = []
        if begDate:
            rows.append(u'Начальная дата периода: %s' % forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s' % forceString(endDate))
        if typeRepN == 0:  # по услуге
            rows.append(u'Услуга: %s' % getActionTypeName(ServiceId))
        elif typeRepN == 1:  # по исполнителю
            if byPerformer:
                if PerformerId:
                    rows.append(u'Исполнитель: %s' % getPersonFIO(PerformerId))
            elif AssistantId:
                rows.append(u'Ассистент: %s' % getPersonFIO(AssistantId))
                if AssistantId2:
                    rows.append(u'Ассистент2: %s' % getPersonFIO(AssistantId2))
                if AssistantId3:
                    rows.append(u'Ассистент3: %s' % getPersonFIO(AssistantId3))
        elif typeRepN == 2:  # по подразделению
            if OrgStrId:
                rows.append(u'Старшее подразделение: %s' % getOrgStructureName(OrgStrId))
            else:
                rows.append(u'Старшее подразделение: ЛПУ')
        elif byCode:  # по пациенту
            rows.append(u'Пациент, код: %s' % forceString(ClientId))
        else:
            rows.append(u'Пациент: %s' % (' '.join([forceString(lastName),
                                                    forceString(firstName),
                                                    forceString(patrName), ]).strip()))
        return rows

    def build(self, params):
        # print params
        typeRep = params['typeRep']
        groupByPatients = params.get('groupByPatients', False)
        self.setTitle(self.basename + ' ' + typeRep[1], "PEDSalaryReports")
        query = self.getData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = self.getCols(typeRep, groupByPatients)
        self.table = createTable(cursor, tableColumns)
        self.fillTable(self.table, params, query)
        return doc

    def getData(self, params):
        typeRepN = params['typeRep'][0]
        begDate = params.get('begDate', QtCore.QDate.currentDate())
        endDate = params.get('endDate', QtCore.QDate.currentDate())
        # endDate         = params.get('endDate', QDate.currentDate()).addDays(1)
        groupByPatients = params.get('groupByPatients', False)
        ServiceId = params.get('ServiceId', None)
        byPerformer = params.get('byPerformer', None)
        PerformerId = params.get('PerformerId', None)
        AssistantId = params.get('AssistantId', None)
        AssistantId2 = params.get('AssistantId2', None)
        AssistantId3 = params.get('AssistantId3', None)
        OrgStrId = params.get('OrgStrId', None)
        ClientId = params.get('ClientId', None)
        db = QtGui.qApp.db

        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableOrgStructureAT = db.table('OrgStructure_ActionType')
        tableContract = db.table('Contract')
        tableFinance = db.table('rbFinance')
        tableClient = db.table('Client')
        tableAccount_Item = db.table('Account_Item')
        # tableATService = db.table('ActionType_Service')
        # tableService = db.table('rbService')
        # tableContractTariff = db.table('Contract_Tariff')
        tablePerson = db.table('Person')

        order = ''
        queryTable = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id'])). \
            innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id'])). \
            innerJoin(tableOrgStructureAT, tableOrgStructureAT['actionType_id'].eq(tableActionType['id'])). \
            innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id'])). \
            innerJoin(tableFinance, db.joinOr([db.joinAnd([tableAction['finance_id'].isNotNull(), \
                                                           tableFinance['id'].eq(tableAction['finance_id'])]), \
                                               tableFinance['id'].eq(tableContract['finance_id'])])). \
            innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id'])). \
            innerJoin(tableAccount_Item, tableAccount_Item['action_id'].eq(tableAction['id']))
        if typeRepN == 1 and (
                        byPerformer and PerformerId or not byPerformer and (
                        AssistantId or AssistantId2 or AssistantId3)):
            if PerformerId:
                queryTable = queryTable.innerJoin(tablePerson,
                                                  db.joinAnd([tablePerson['deleted'].eq(0), tablePerson['id']. \
                                                             eq(tableAction['person_id'])]))
            else:
                assists_cond = [tablePerson['deleted'].eq(0), ]
                assistCondTemplate = u"EXISTS(SELECT A_A.id " \
                                     u"      FROM Action_Assistant AS A_A " \
                                     u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id " \
                                     u"       WHERE A_A.action_id = %s " \
                                     u"              AND rbAAT.code like '%s' " \
                                     u"              AND A_A.person_id = %s" \
                                     u"       LIMIT 1)"
                if AssistantId:
                    assists_cond.append(assistCondTemplate % (tableAction['id'].name(),
                                                              u'assistant',
                                                              tablePerson['id'].name()))
                if AssistantId2:
                    assists_cond.append(assistCondTemplate % (tableAction['id'].name(),
                                                              u'assistant2',
                                                              tablePerson['id'].name()))
                if AssistantId3:
                    assists_cond.append(assistCondTemplate % (tableAction['id'].name(),
                                                              u'assistant3',
                                                              tablePerson['id'].name()))
                queryTable = queryTable.innerJoin(tablePerson,
                                                  db.joinAnd([tablePerson['deleted'].eq(0), db.joinOr(assists_cond)]))
        else:
            queryTable = queryTable.innerJoin(tablePerson,
                                              db.joinAnd([tablePerson['deleted'].eq(0),
                                                          db.joinOr([tablePerson['id'].eq(tableAction['person_id']),
                                                                     "%s IN (SELECT Action_Assistant.person_id " \
                                                                     "       FROM Action_Assistant "
                                                                     "             INNER JOIN rbActionAssistantType AS aType ON aType.id = Action_Assistant.assistantType_id"
                                                                     "       WHERE Action_Assistant.action_id = %s "
                                                                     "             AND aType.code IN ('assistant', 'assistant2', 'assistant3'))"
                                                                     % (tablePerson['id'].name(), tableAction['id'])
                                                                     ])]))

        fields = [tableOrgStructureAT['master_id'].alias('OrgStrId'),
                  #                  tableActionType['code'].alias('ServiceCode'),
                  tableActionType['name'].alias('ServiceName'),
                  tableAccount_Item['amount'].alias(
                      'ServiceAmount') if typeRepN != 2 else 'SUM(`Account_Item`.`amount`) AS `ServiceAmount`',
                  #                  tableAction['payStatus'],
                  #                  tableFinance['code'].alias('financeCode'),
                  tableAccount_Item['price'],
                  tablePerson['id'].alias('PerformerId'),
                  tablePerson['lastName'].alias('PerformerLastName'),
                  tablePerson['firstName'].alias('PerformerFirstName'),
                  tablePerson['patrName'].alias('PerformerPatrName'),
                  #                  u"IF(Action.assistant_id IS NOT NULL AND Action.assistant_id = Person.id, Action.id+1000000,Action.id) AS ActionId",
                  ]
        if groupByPatients:
            fields += [tableClient['id'].alias('client_id'),
                       tableClient['lastName'].alias('ClientLastName'),
                       tableClient['firstName'].alias('ClientFirstName'),
                       tableClient['patrName'].alias('ClientPatrName'), ]
            order = 'ClientLastName,ClientFirstName,ClientPatrName,'
        # payStatusCond = db.joinOr(["Action.payStatus & POW(2,2*rbFinance.code)*2 = POW(2,2*rbFinance.code)*2",
        #                          "Action.payStatus & POW(2,2*rbFinance.code)*3 = POW(2,2*rbFinance.code)*3"])
        if typeRepN == 0:  # по услуге
            order += 'PerformerLastName,PerformerFirstName,PerformerPatrName,PerformerId,'
        if typeRepN == 1 or typeRepN == 2:  # по исполнителю / по подразделению
            fields += ["""(SELECT A_A.person_id
                            FROM Action_Assistant AS A_A
                            INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                            WHERE A_A.action_id =  %s AND rbAAT.code like 'assistant'
                            LIMIT 1) AS assistant_id
                        """ % tableAction['id'].name(),
                       """(SELECT A_A.person_id
                           FROM Action_Assistant AS A_A
                           INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                           WHERE A_A.action_id = %s AND rbAAT.code like 'assistant2'
                           LIMIT 1) AS assistant2_id
                       """ % tableAction['id'].name(),
                       """(SELECT A_A.person_id
                           FROM Action_Assistant AS A_A
                           INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                           WHERE A_A.action_id = %s AND rbAAT.code like 'assistant3'
                           LIMIT 1) AS assistant3_id
                       """ % tableAction['id'].name()
                       ]
        if typeRepN == 1:  # по исполнителю
            order += 'PerformerLastName,PerformerFirstName,PerformerPatrName,PerformerId,assistant_id,OrgStrId,'
        elif typeRepN == 2:  # по подразделению
            order += 'PerformerLastName,PerformerFirstName,PerformerPatrName,ServiceName,PerformerId,assistant_id,'
        cond = [tableEvent['deleted'].eq(0),
                tableAction['deleted'].eq(0),
                tableActionType['deleted'].eq(0),
                tableClient['deleted'].eq(0),
                tableContract['deleted'].eq(0),
                tableEvent['deleted'].eq(0),
                tableAccount_Item['date'].ge(begDate),
                tableAccount_Item['date'].le(endDate),
                "Action.payStatus & POW(2,2*rbFinance.code)*3 = POW(2,2*rbFinance.code)*3",
                ]
        order += 'ServiceName'
        #        if typeRepN != 1:
        #            order += ',payStatus'
        if typeRepN == 0:  # по услуге
            cond.insert(0, tableActionType['id'].eq(ServiceId))
        if typeRepN == 2:  # по подразделению
            if OrgStrId:
                print forceString(OrgStrId)
                cond.insert(0, tableOrgStructureAT['master_id'].inlist(getOrgStructureDescendants(OrgStrId)))
        else:
            if typeRepN == 1:  # по исполнителю
                if byPerformer:
                    if PerformerId:
                        cond.insert(0, tableAction['person_id'].eq(PerformerId))
                else:
                    assistCondTemplate = u"EXISTS(SELECT A_A.id " \
                                         u"      FROM Action_Assistant AS A_A " \
                                         u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id " \
                                         u"       WHERE A_A.action_id = %s " \
                                         u"              AND rbAAT.code like '%s' " \
                                         u"              AND A_A.person_id = %s" \
                                         u"       LIMIT 1)"
                    if AssistantId3:
                        cond.insert(0, assistCondTemplate % (tableAction['id'].name(),
                                                             'assistant3',
                                                             AssistantId3))
                    if AssistantId2:
                        cond.insert(0, assistCondTemplate % (tableAction['id'].name(),
                                                             'assistant2',
                                                             AssistantId2))
                    if AssistantId:
                        cond.insert(0, assistCondTemplate % (tableAction['id'].name(),
                                                             'assistant',
                                                             AssistantId))
            elif typeRepN == 3:  # по пациенту
                cond.insert(0, tableClient['id'].eq(ClientId))
        stmt = db.selectStmt(
            queryTable,
            fields,
            cond,
            order=order,
            group=['`PerformerLastName`', '`price`', '`ServiceName`']
        )

        # if typeRepN == 2:
        #    return fastQuerySalaryReport(stmt)

        print stmt
        return db.query(stmt)

    def getCols(self, typeRep, groupByPatients):
        cols = [('', [u'№'], CReportBase.AlignRight),
                ('', [u'Пациент'], CReportBase.AlignLeft),
                ('', [u'Подразделение'], CReportBase.AlignLeft),
                ('', [u'ФИО исполнителя'], CReportBase.AlignLeft),
                #                ('',[u'Код услуги'], CReportBase.AlignLeft),
                ('', [u'Наименование услуги'], CReportBase.AlignLeft),
                ('', [u'Кол-во'], CReportBase.AlignLeft),
                #                ('',[u'Состояние оплаты'], CReportBase.AlignLeft),
                ('', [u'Цена'], CReportBase.AlignLeft),
                ('', [u'Сумма'], CReportBase.AlignLeft), ]
        if typeRep[0] == 1:  # По исполнителю
            cols.insert(2, cols.pop(3))  # ФИО исполнителя перед Подразделением
        # del cols[7] # -Состояние оплаты
        if typeRep[0] == 0:  # По услуге
            pass
        # del cols[4] # -Наименование услуги
        #            del cols[4] # -Код услуги
        if not groupByPatients:
            del cols[1]  # -Пациент
        # if typeRep[0] == 1: # По исполнителю
        #            del cols[2] # -Исполнитель
        if (typeRep[0] == 2):  # По подразделению
            del cols[1]  # -Подразделение
        self.colnames = map(lambda col: col[1][0], cols)[1:]
        self.n2i = dict(map(lambda col, num: [col[1][0], num], cols, xrange(len(cols))))
        self.i2n = dict(map(lambda col, num: [num, col[1][0]], cols, xrange(len(cols))))
        ReportColumnBase.valuemap = []
        ReportColumnBase.insts = {}
        ReportColumnBase.rownum = 0
        ReportColumnBase.parent = self
        self.insts = {
            u'Пациент': ReportColumnPatient(
                expandLimCol=u'Пациент' in self.colnames and self.n2i[u'Пациент'] != 1 and self.i2n[
                    self.n2i[u'Пациент'] - 1] or None),
            u'Подразделение': ReportColumnStructure(
                expandLimCol=u'Подразделение' in self.colnames and self.n2i[u'Подразделение'] != 1 and self.i2n[
                    self.n2i[u'Подразделение'] - 1] or None),
            u'ФИО исполнителя': ReportColumnPerformer(
                expandLimCol=u'ФИО исполнителя' in self.colnames and self.n2i[u'ФИО исполнителя'] != 1 and self.i2n[
                    self.n2i[u'ФИО исполнителя'] - 1] or None),
            u'Наименование услуги': ReportColumnService(
                expandLimCol=u'Наименование услуги' in self.colnames and self.n2i[u'Наименование услуги'] != 1 and
                             self.i2n[self.n2i[u'Наименование услуги'] - 1] or None),
            u'Кол-во': ReportColumnAmount(expandLimCol=u'Наименование услуги'),
            u'Цена': ReportColumnPrice(expand=False),
            u'Сумма': ReportColumnSum(expandLimCol=u'Наименование услуги'),
        }
        iter = 50
        while ReportColumnBase.queue and iter > 0:
            iter -= 1
            q = ReportColumnBase.queue.pop(0)
            eval(q)
        if not iter:
            print 'Iteration limit overflow with:', q
        self.onlyMatterCols = [u'Пациент', u'Подразделение', u'ФИО исполнителя', u'Наименование услуги',
                               u'Цена', ]  # []
        #        self.onlyMatterCols = map(lambda col: col in onlyMatterCols and col or None, self.colnames)
        #        for i in xrange(len(self.colnames)):
        #            print self.colnames[i], self.onlyMatterCols[i]
        self.colinst = map(lambda col: self.insts[col], self.colnames)
        return cols

    def setText(self, row, col, val):
        if isinstance(val, DictType):
            val = val['val']
        if val is not None:
            self.table.setText(row, col, val)

    def fillTable(self, table, params, query):
        #        typeRepN = params['typeRep'][0]
        print 'filling...'
        while query.next():  # and t <= 100:
            ReportColumnBase.record = query.record()
            ReportColumnBase.row = {'type': 'normal',}
            ReportColumnBase.queue = []
            map(lambda i: i.set(), self.colinst)
            diff = False
            if not ReportColumnBase.valuemap:
                diff = True
            else:
                for k in ReportColumnBase.row.keys():
                    if k in self.onlyMatterCols:
                        if ReportColumnBase.row[k] != ReportColumnBase.valuemap[-1][k]:
                            diff = True
                            break
            if diff:
                ReportColumnBase.addRow()
            else:
                map(lambda i: i.merge(), self.colinst)
            for q in ReportColumnBase.queue:
                eval(q)
        ReportColumnBase.insts[u'ФИО исполнителя'].subSum(True, forceInt(params.get('typeRep')[0]))
        ReportColumnBase.addSumRow()
        #        myf = copen('C:/temp/tmp.txt', 'w', 'utf8') ###
        #        for i in xrange(len(ReportColumnBase.valuemap)):
        #            myf.write(u"%4d ФИО исполнителя: %20s ассистент: %5s, Подразделение:%20s, Кол-во: %3s, Цена: %8s, Сумма: %9s, Тип: %6s, Услуга: %s\n"%
        #                          (i,
        #                          unicode(ReportColumnBase.valuemap[i][u'ФИО исполнителя']['val']),
        #                          ReportColumnBase.valuemap[i][u'ФИО исполнителя'].has_key('opt') and
        #                            unicode(ReportColumnBase.valuemap[i][u'ФИО исполнителя']['opt']) or '',
        #                          unicode(ReportColumnBase.valuemap[i][u'Подразделение']['val']),
        #                          unicode(ReportColumnBase.valuemap[i][u'Кол-во']),
        #                          unicode(ReportColumnBase.valuemap[i][u'Цена']),
        #                          unicode(ReportColumnBase.valuemap[i][u'Сумма']),
        #                          unicode(ReportColumnBase.valuemap[i][u'type']),
        #                          unicode(ReportColumnBase.valuemap[i][u'Наименование услуги']),
        #                          ))
        #
        #        myf.close()
        if ReportColumnBase.valuemap:
            print 'making table view...'
            n = 1
            st = 1
            numsRow = dict(map(lambda col: [col, st], self.colnames))
            summPrice = 0
            summNumber = 0
            rowName = ''
            oldRowName = ''
            for i in xrange(len(ReportColumnBase.valuemap)):
                ReportColumnBase.rownum = i
                type = ReportColumnBase.valuemap[i]['type']
                stind = ReportColumnBase.valuemap[i].get('stind', 999)
                show = ReportColumnBase.valuemap[i].get('show', [])
                hide = ReportColumnBase.valuemap[i].get('hide', [])
                mergeTo = ReportColumnBase.valuemap[i].get('mergeTo', '')
                row = dict(map(lambda inst: [inst.name, inst.get()], self.colinst))

                # В Отчете по подразделению сие не нужно (i3272)
                if params['typeRep'][0] != 2:
                    if n == 1:
                        oldRowName = forceString(row[u'Подразделение'])
                    rowName = forceString(row[u'Подразделение'])

                flagSumm = False
                if rowName != oldRowName:
                    rownum = table.addRow()
                    if forceInt(params.get('typeRep')[0]) != 1:
                        self.setText(rownum, 2, u'Итого')
                    else:
                        self.setText(rownum, 3, u'Итого')
                    self.setText(rownum, 4, summNumber)
                    self.setText(rownum, 6, summPrice)
                    summNumber = 0
                    summPrice = 0
                    oldRowName = forceString(row[u'Подразделение'])
                    flagSumm = True
                if type == 'normal' and not mergeTo:
                    summNumber += forceInt(row[u'Кол-во'])
                    summPrice += forceDouble(row[u'Сумма'])
                rownum = table.addRow()
                if rownum == st:
                    self.setText(rownum, self.n2i[u'№'], n)
                    n += 1
                    for col in self.colnames:
                        if type == 'normal' or show and col in show or not show and col not in hide:
                            self.setText(rownum, self.n2i[col], row[col])
                else:
                    if self.insts[self.i2n[1]].expand:
                        if lastRow[self.i2n[1]] != row[self.i2n[1]] or type != ReportColumnBase.valuemap[i - 1][
                            'type'] and stind == 0:
                            self.setText(rownum, self.n2i[u'№'], n)
                            n += 1
                            table.mergeCells(numsRow[self.i2n[1]], self.n2i[u'№'], rownum - numsRow[self.i2n[1]], 1)
                    else:
                        self.setText(rownum, self.n2i[u'№'], n)
                        n += 1
                    for col in self.colnames:
                        if self.insts[col].expand:
                            if lastRow[col] != row[col] or type != 'normal' and self.n2i[col] > stind:
                                expandChilds = self.insts[col].getExpandChilds()
                                for cl in [col, ] + expandChilds:
                                    if numsRow[cl] != rownum:  # Если ячейка была инициализирована родительским столбцом
                                        if cl == u'Подразделение' or cl == u'ФИО исполнителя' and not flagSumm:
                                            table.mergeCells(numsRow[cl], self.n2i[cl], rownum - numsRow[cl], 1)
                                        else:
                                            table.mergeCells(numsRow[cl], self.n2i[cl], rownum - numsRow[cl] - 1, 1)
                                        numsRow[cl] = rownum
                                        if type == 'normal' or show and cl in show or not show and cl not in hide:
                                            self.setText(rownum, self.n2i[cl], row[cl])
                        else:
                            if type == 'normal' or show and col in show or not show and col not in hide:
                                self.setText(rownum, self.n2i[col], row[col])
                        if type != 'normal' and mergeTo:
                            table.mergeCells(rownum, stind, 1, mergeTo - stind)
                lastRow = row


class ReportColumnBase:
    parent = None
    record = None
    insts = {}
    valuemap = []
    rownum = 0
    row = {}
    queue = []

    def __init__(self, name, queryCol='', queryColNormFunc=None, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.insts[name] = self
        self.expandChilds = []
        self.queryCol = queryCol
        self.queryColNormFunc = queryColNormFunc
        self.SHOW_NULLS = showNulls
        self.name = name
        self.expand = expand
        self.expandLimCol = expandLimCol
        self.allExpandChilds = None
        self.expandParents = None
        if expandLimCol and expandLimCol in self.parent.colnames:
            if not ReportColumnBase.insts.has_key(expandLimCol):
                ReportColumnBase.queue.append(
                    "ReportColumnBase.insts.has_key(u'%s') and ReportColumnBase.insts[u'%s'].expandChilds.append(u'%s') or not ReportColumnBase.insts.has_key(u'%s') and ReportColumnBase.queue.append(q)" % (
                        expandLimCol, expandLimCol, name, expandLimCol))
            else:
                ReportColumnBase.insts[expandLimCol].expandChilds.append(name)

    @staticmethod
    def addRow(row=None, before=None):
        if row is None:
            row = ReportColumnBase.row
        if before is None:
            ReportColumnBase.valuemap.append(row)
        else:
            ReportColumnBase.valuemap.insert(before, row)
        ReportColumnBase.rownum += 1
        ReportColumnBase.row = {}

    def get(self, rownum=None):
        if rownum == None:
            rownum = self.rownum
        return self.valuemap[rownum][self.name]

    def getExpandChilds(self):
        if self.allExpandChilds is None:
            childs = self.expandChilds + []
            for child in self.expandChilds:
                childs += ReportColumnBase.insts[child].getExpandChilds()
            self.allExpandChilds = childs
        return self.allExpandChilds

    def getExpandParents(self):
        if self.expandParents is None:
            if self.expandLimCol:
                parents = [self.expandLimCol, ] + ReportColumnBase.insts[self.expandLimCol].getExpandParents()
            else:
                parents = []
            self.expandParents = parents
        return self.expandParents

    def set(self):
        self.row[self.name] = self.queryColNormFunc(self.record.value(self.queryCol))

    def merge(self, rownum=None):
        if rownum == None:
            rownum = self.rownum
        self.valuemap[-1][self.name] = self.row[self.name]

    def getRowRange(self, row=None, colName=None):
        MIN = 0
        MAX = len(self.valuemap)
        if row is None:
            row = self.rownum
        if colName is None:
            colName = self.name
        minRow = maxRow = baseRow = row
        exceedMax = exceedMin = False
        if colName in self.getExpandParents():
            cols = self.getExpandParents()
        else:
            cols = [colName, ] + self.getExpandParents()
        valsToCmp = map(lambda colName: self.valuemap[row][colName], cols)
        row += 1
        while not exceedMax and row < maxRow:
            for i in xrange(len(cols)):
                if self.valuemap[row][cols[i]] != valsToCmp[i]:
                    exceedMax = True
                    break
            if not exceedMax:
                maxRow = row
            row += 1
        row = baseRow - 1
        while not exceedMin and abs(row) < minRow:
            for i in xrange(len(cols)):
                if self.valuemap[row][cols[i]] != valsToCmp[i]:
                    exceedMin = True
                    break
            if not exceedMin:
                minRow = row
            row -= 1
        return minRow, maxRow

    def getBlockSum(self, min=None, max=None, colName=None, type=None, skiptypes=None):
        if not skiptypes:
            skiptypes = []
        if min is None: min = 0
        if max is None: len(self.valuemap) - 1
        if colName is None:
            colName = self.name
        hasNone = False
        sum = 0
        for i in xrange(min, max + 1):
            show = self.valuemap[i].get('show', [])
            hide = self.valuemap[i].get('hide', [])
            if not show and not hide or hide and colName not in hide or not hide and show and colName in show:
                if (type and self.valuemap[i]['type'] == type) or \
                        (not type and not skiptypes) or \
                        (not type and skiptypes and self.valuemap[i]['type'] not in skiptypes):
                    if isinstance(self.valuemap[i][colName], DictType):
                        val = self.valuemap[i][colName]['val']
                    else:
                        val = self.valuemap[i][colName]
                    if val is not None:
                        sum += val
                    else:
                        hasNone = True
            elif hide and colName not in hide or not hide and show and colName in show:
                hasNone = True
        if hasNone and sum == 0:
            sum = None
        return sum

    @staticmethod
    def addSumRow():
        if len(ReportColumnBase.valuemap):
            min, max = 0, len(ReportColumnBase.valuemap) - 1
            row = copy(ReportColumnBase.valuemap[-1])
            row['stind'] = 1
            perffollowingcol = ReportColumnBase.parent.i2n[1]
            row['type'] = 'subsum'
            row['show'] = [perffollowingcol, u'Кол-во', u'Сумма']
            row['mergeTo'] = ReportColumnBase.parent.n2i[u'Кол-во']
            if isinstance(row[perffollowingcol], DictType):
                row[perffollowingcol] = {'val': u'ИТОГО'}
            else:
                row[perffollowingcol] = u'ИТОГО'
            row[u'Кол-во'] = ReportColumnBase.getBlockSum(ReportColumnBase.insts.values()[0], min, max,
                                                          colName=u'Кол-во', type='normal')
            row[u'Сумма'] = ReportColumnBase.getBlockSum(ReportColumnBase.insts.values()[0], min, max, colName=u'Сумма',
                                                         type='normal')
            ReportColumnBase.addRow(row)


class ReportColumnPatient(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'Пациент', None, None, expand, expandLimCol, showNulls)

    def set(self):
        client_id = forceRef(self.record.value('client_id'))  #
        ClientLastName = forceString(self.record.value('ClientLastName'))
        ClientFirstName = forceString(self.record.value('ClientFirstName'))
        ClientPatrName = forceString(self.record.value('ClientPatrName'))
        self.row[self.name] = {'id': client_id, 'val': getShortFIO(ClientLastName, ClientFirstName, ClientPatrName)}

    def get(self, rownum=None):
        if rownum == None:
            rownum = self.rownum
        return self.valuemap[rownum][self.name]['val']


class ReportColumnStructure(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'Подразделение', None, None, expand, expandLimCol, showNulls)
        self.OrgStrs = {None: u'ЛПУ',}

    def set(self):
        OrgStrId = forceRef(self.record.value('OrgStrId'))
        if OrgStrId not in self.OrgStrs:
            self.OrgStrs[OrgStrId] = getOrgStructureName(OrgStrId)
        self.row[self.name] = {'id': OrgStrId, 'val': self.OrgStrs[OrgStrId]}

    def get(self, rownum=None):
        if rownum == None:
            rownum = self.rownum
        return self.valuemap[rownum][self.name]['val']


class ReportColumnPerformer(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'ФИО исполнителя', None, None, expand, expandLimCol, showNulls)

    def set(self):
        PerformerId = forceInt(self.record.value('PerformerId'))  #
        AssistantId = forceInt(self.record.value('assistant_id'))  #
        AssistantId2 = forceInt(self.record.value('assistant2_id'))  #
        AssistantId3 = forceInt(self.record.value('assistant3_id'))  #
        assist = False
        if PerformerId in (AssistantId, AssistantId2, AssistantId3,):
            assist = True
        PerformerLastName = forceString(self.record.value('PerformerLastName'))
        PerformerFirstName = forceString(self.record.value('PerformerFirstName'))
        PerformerPatrName = forceString(self.record.value('PerformerPatrName'))
        if assist:
            self.row['type'] = 'assist'
            # self.row['stind'] = self.parent.n2i[u'ФИО исполнителя']-1
            self.row['hide'] = [u'Цена', u'Сумма', ]
            # self.row[self.name] = {'id':PerformerId, 'val':getShortFIO(PerformerLastName, PerformerFirstName, PerformerPatrName)+' ', 'opt':assist}
        # else:
        self.row[self.name] = {'id': PerformerId,
                               'val': getShortFIO(PerformerLastName, PerformerFirstName, PerformerPatrName),
                               'opt': assist}
        if self.valuemap and self.row[self.name] != self.valuemap[-1][self.name]:
            self.queue.append("ReportColumnBase.insts[u'%s'].subSum()" % self.name)

    def get(self, rownum=None):
        if rownum == None:
            rownum = self.rownum
        return self.valuemap[rownum][self.name]  # ['val']

    def getassist(self, rownum=None):
        if rownum == None:
            rownum = self.rownum
        return self.valuemap[rownum][self.name]['opt']

    def subSum(self, finalRow=False, typeRep=0):
        # if typeRep == 2:
        #     if finalRow :
        #         if self.valuemap[-2][self.name] != self.valuemap[-1][self.name]:
        #             return
        lastBlockRow = len(self.valuemap) - 2
        if lastBlockRow > 0:
            min, max = self.getRowRange(lastBlockRow)
            if max - min > 0:
                row = copy(self.valuemap[-2])
                row['stind'] = self.parent.n2i[u'Наименование услуги']
                perffollowingcol = self.parent.i2n[row['stind']]
                row['type'] = 'subsum'
                if row[u'ФИО исполнителя']['opt']:
                    row['show'] = [perffollowingcol, u'Кол-во']
                else:
                    row['show'] = [perffollowingcol, u'Кол-во', u'Сумма']
                row['mergeTo'] = self.parent.n2i[u'Кол-во']
                if isinstance(row[perffollowingcol], DictType):
                    row[perffollowingcol] = {'val': u'Итого'}
                else:
                    row[perffollowingcol] = u'Итого'
                row[u'Кол-во'] = self.getBlockSum(min, max, colName=u'Кол-во')
                row[u'Сумма'] = self.getBlockSum(min, max, colName=u'Сумма')
                #                print row[u'Кол-во'], row[u'Сумма']
                #                for i in self.parent.colnames[row['stind']:]:
                #                    if i not in [perffollowingcol,u'Кол-во',u'Сумма',]:
                #                        row[i] = None
                self.addRow(row, None if finalRow else -1)


class ReportColumnService(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'Наименование услуги', 'ServiceName', forceString, expand, expandLimCol,
                                  showNulls)


class ReportColumnAmount(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'Кол-во', 'ServiceAmount', forceInt, expand, expandLimCol, showNulls)

    def get(self, rownum=None):
        if rownum is None:
            rownum = self.rownum
        if self.valuemap[rownum]['type'] != 'subsum':
            min, max = self.getRowRange(rownum, u'Наименование услуги')
            return self.getBlockSum(min, max)
        else:  # if self.valuemap[rownum]['type'] == 'subsum':
            return self.valuemap[rownum][self.name]

    def merge(self, rownum=None):
        self.valuemap[-1][self.name] += self.row[self.name]


class ReportColumnPrice(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'Цена', 'price', forceDouble, expand, expandLimCol, showNulls)
        #    def set(self):
        #        if self.row.has_key(u'ФИО исполнителя') and not self.row[u'ФИО исполнителя']['opt']:
        #            price = forceDouble(self.record.value('price'))
        #        else:
        #            price = None
        #        self.row[u'Цена'] = price


class ReportColumnSum(ReportColumnBase):
    def __init__(self, expand=True, expandLimCol=None, showNulls=False):
        ReportColumnBase.__init__(self, u'Сумма', None, None, expand, expandLimCol, showNulls)

    def set(self):
        if self.row.has_key(u'ФИО исполнителя'):
            if self.row.has_key(u'Кол-во'):
                ServiceAmount = self.row[u'Кол-во']
            else:
                ServiceAmount = forceInt(self.record.value('ServiceAmount'))
            if self.row.has_key(u'Цена'):
                price = self.row[u'Цена']
            else:
                price = forceDouble(self.record.value('price'))
            sum = ServiceAmount * price
            self.row[self.name] = sum
        else:
            self.queue.append("ReportColumnBase.insts[u'%s'].set()" % self.name)

    def get(self, rownum=None):
        if rownum is None:
            rownum = self.rownum
        if self.valuemap[rownum]['type'] != 'subsum':
            min, max = self.getRowRange(rownum, u'Наименование услуги')
            return self.getBlockSum(min, max)
        else:  # if self.valuemap[rownum]['type'] == 'subsum':
            return self.valuemap[rownum][self.name]

    def merge(self, rownum=None):
        if not (self.valuemap[-1][self.name] is None or self.row[self.name] is None):
            self.valuemap[-1][self.name] += self.row[self.name]


class CPEDSalaryReportsSetupDialog(QtGui.QDialog, Ui_PEDSalaryReportsSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.byPerformer = True
        self.byCode = True
        self.ClientId = None

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        # print params
        typeRep = params.get('typeRep', [0, ])[0]
        self.chkGroupByPatients.setChecked(params.get('groupByPatients', False))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('OrgStrId', None))
        self.cmbService.setValue(params.get('ServiceId', None))
        self.byPerformer = params.get('byPerformer', True)
        self.radioPerformer.setChecked(self.byPerformer)
        self.radioAssistant.setChecked(not self.byPerformer)
        self.cmbPerformer.setValue(params.get('PerformerId', None))
        self.cmbAssistant.setValue(params.get('AssistantId', None))
        self.cmbAssistant2.setValue(params.get('AssistantId2', None))
        self.cmbAssistant3.setValue(params.get('AssistantId3', None))
        self.byCode = params.get('byCode', True)
        self.chkCode.setChecked(self.byCode)
        self.editAmbCard.setText(forceString(params.get('ClientId', '')))
        self.editLastName.setText(params.get('lastName', ''))
        self.editFirstName.setText(params.get('firstName', ''))
        self.editPatrName.setText(params.get('patrName', ''))
        if typeRep == 0:
            self.radioByService.setChecked(True)
            self.on_radioByService_clicked(True)
        elif typeRep == 1:
            self.radioByPerformer.setChecked(True)
            self.on_radioByPerformer_clicked(True)
        elif typeRep == 2:
            self.radioByStructure.setChecked(True)
            self.on_radioByStructure_clicked(True)
        else:
            self.radioByPatient.setChecked(True)
            self.on_radioByPatient_clicked(True)

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['ServiceId'] = self.cmbService.value()
        params['groupByPatients'] = self.chkGroupByPatients.isEnabled() and self.chkGroupByPatients.isChecked()
        params['PerformerId'] = self.cmbPerformer.value()
        params['AssistantId'] = self.cmbAssistant.value()
        params['AssistantId2'] = self.cmbAssistant2.value()
        params['AssistantId3'] = self.cmbAssistant3.value()
        params['OrgStrId'] = self.cmbOrgStructure.value()
        params['ClientId'] = self.ClientId
        params['lastName'] = self.editLastName.text()
        params['firstName'] = self.editFirstName.text()
        params['patrName'] = self.editPatrName.text()
        params['byPerformer'] = self.radioPerformer.isChecked()
        params['byCode'] = self.chkCode.isChecked()
        if self.radioByService.isChecked():
            params['typeRep'] = (0, u'по услуге')
        elif self.radioByPerformer.isChecked():
            params['typeRep'] = (1, u'по исполнителю')
        elif self.radioByStructure.isChecked():
            params['typeRep'] = (2, u'по подразделению')
        else:
            params['typeRep'] = (3, u'по пациенту')
        return params

    @QtCore.pyqtSlot(bool)
    def on_radioByService_clicked(self, value):
        # CheckBox Группировать по пациентам / Услугам
        self.chkGroupByPatients.setEnabled(True)
        # Подразделение
        self.lblOrgStructure.setEnabled(False)
        self.cmbOrgStructure.setEnabled(False)
        # Услуга
        self.lblService.setEnabled(True)
        self.cmbService.setEnabled(True)
        # Widget Исполнителя/Ассистента
        self.wgtByPerformer.setEnabled(False)
        # GroupBox Пациенты
        self.grbPatient.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_radioByPerformer_clicked(self, value):
        # CheckBox Группировать по пациентам / Услугам
        self.chkGroupByPatients.setEnabled(False)
        # Подразделение
        self.lblOrgStructure.setEnabled(False)
        self.cmbOrgStructure.setEnabled(False)
        # Услуга
        self.lblService.setEnabled(False)
        self.cmbService.setEnabled(False)
        # Widget Исполнителя/Ассистента
        self.wgtByPerformer.setEnabled(True)
        self.radioPerformer.setEnabled(True)
        self.radioAssistant.setEnabled(True)
        self.cmbPerformer.setEnabled(self.byPerformer)
        self.cmbAssistant.setEnabled(not self.byPerformer)
        self.cmbAssistant2.setEnabled(not self.byPerformer)
        self.cmbAssistant3.setEnabled(not self.byPerformer)
        # GroupBox Пациенты
        self.grbPatient.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_radioByStructure_clicked(self, value):
        # CheckBox Группировать по пациентам / Услугам
        self.chkGroupByPatients.setEnabled(True)
        # Подразделение
        self.lblOrgStructure.setEnabled(True)
        self.cmbOrgStructure.setEnabled(True)
        # Услуга
        self.lblService.setEnabled(False)
        self.cmbService.setEnabled(False)
        # Widget Исполнителя/Ассистента
        self.wgtByPerformer.setEnabled(False)
        # GroupBox Пациенты
        self.grbPatient.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_radioByPatient_clicked(self, value):
        # CheckBox Группировать по пациентам / Услугам
        self.chkGroupByPatients.setEnabled(False)
        # Подразделение
        self.lblOrgStructure.setEnabled(False)
        self.cmbOrgStructure.setEnabled(False)
        # Услуга
        self.lblService.setEnabled(False)
        self.cmbService.setEnabled(False)
        # Widget Исполнителя/Ассистента
        self.wgtByPerformer.setEnabled(False)
        # GroupBox Пациенты
        self.grbPatient.setEnabled(True)
        self.editAmbCard.setEnabled(self.byCode)
        self.editLastName.setEnabled(not self.byCode)
        self.editFirstName.setEnabled(not self.byCode)
        self.editPatrName.setEnabled(not self.byCode)

    @QtCore.pyqtSlot(bool)
    def on_radioPerformer_toggled(self, value):
        self.byPerformer = value
        self.cmbPerformer.setEnabled(value)
        self.cmbAssistant.setEnabled(not value)
        self.cmbAssistant2.setEnabled(not value)
        self.cmbAssistant3.setEnabled(not value)

    @QtCore.pyqtSlot(bool)
    def on_chkCode_toggled(self, value):
        self.byCode = value
        self.editAmbCard.setEnabled(value)
        self.editLastName.setEnabled(not value)
        self.editFirstName.setEnabled(not value)
        self.editPatrName.setEnabled(not value)

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        msg = u''
        if not self.edtBegDate.date().isValid() or not self.edtEndDate.date().isValid() or self.edtBegDate.date() > self.edtEndDate.date():
            msg = u'Неверно задан период. '
        if self.radioByService.isChecked():
            if not self.cmbService.value():
                msg += u'Необходимо выбрать услугу. '
        elif self.radioByPerformer.isChecked():
            pass
        # if self.byPerformer:
        #                if not self.cmbPerformer.value():
        #                    msg += u'Необходимо выбрать исполнителя. '
        #            elif not self.cmbAssistant.value():
        #                msg += u'Необходимо выбрать ассистента. '
        elif self.radioByStructure.isChecked():
            pass
        # if not self.cmbOrgStructure.value():
        #                msg += u'Необходимо выбрать подразделение. '
        else:
            db = QtGui.qApp.db
            tClient = db.table('Client')
            if self.byCode:
                self.ClientId = self.editAmbCard.text()
                record = db.getRecordEx(tClient, [tClient['id']],
                                        [tClient['id'].eq(self.ClientId), ])
                if record is None:
                    msg += u'Пациента с таким кодом не существует! '
                else:
                    self.ClientId = forceRef(record.value('id'))
            else:
                lastName = self.editLastName.text()
                firstName = self.editFirstName.text()
                patrName = self.editPatrName.text()
                record = db.getRecordEx(tClient, [tClient['id']],
                                        [tClient['lastName'].eq(lastName),
                                         tClient['firstName'].eq(firstName),
                                         tClient['patrName'].eq(patrName), ])
                if record is None:
                    msg += u'Пациента с таким ФИО не существует! '
                else:
                    self.ClientId = forceRef(record.value('id'))
        if msg:
            QtGui.QMessageBox.critical(self, u'Внимание!', msg)
        else:
            self.accept()
