# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrganisationMainStaff
from Reports.ReportBase import createAutographField, createTable, CReportBase
from Reports.ReportView import CReportViewDialog
from Ui_ReportAccountService import Ui_ReportAccount
from Ui_ReportAccountService_InsurerForm import Ui_Form
from library.Utils import forceDate, forceDouble, forceInt, forceRef, forceString, formatName


def selectData(accountItemIdList, financeId, insurerList=None, advanced=False, params=None):
    db = QtGui.qApp.db
    groupType = 'client'
    if params is not None:
        dateType = params.get('dateType', 'account')
        begDate = params.get('begDate', QtCore.QDate.currentDate())
        endDate = params.get('endDate', QtCore.QDate.currentDate())
        financeDict = params.get('finance', None)
        financeList = financeDict.keys()
        insurerList = params.get('insurerList', ([], []))
        groupType = params.get('groupType', 'client')

    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableAction = db.table('Action')
    tableOrganisation = db.table('Organisation').alias('Insurer')

    if insurerList:
        insurerInList, insurerNotInList = insurerList
    else:
        insurerInList, insurerNotInList = [], []

    cond = [tableAccountItem['deleted'].eq(0)]

    finanseCode = ''
    if not advanced:
        finanseCode = forceString(db.translate('rbFinance', 'id', financeId, 'code'))
        cond.append(tableAccountItem['id'].inlist(accountItemIdList))
        if insurerInList:
            cond.append(tableOrganisation['id'].inlist(insurerInList))
        if insurerNotInList:
            cond.append(tableOrganisation['id'].notInlist(insurerInList))
    else:
        if dateType == 'account':
            cond.extend([tableAccount['settleDate'].dateGe(begDate), tableAccount['settleDate'].dateLe(endDate)])
        else:
            cond.extend([tableAction['begDate'].dateGe(begDate), tableAction['endDate'].dateLe(endDate)])
        if financeList:
            tableContract = db.table('Contract')
            cond.append(tableContract['finance_id'].inlist(financeList))
        if insurerInList:
            cond.append(tableOrganisation['id'].inlist(insurerInList))
        if insurerNotInList:
            cond.append(tableOrganisation['id'].notInlist(insurerNotInList))

    if advanced:
        advancedSelect = ''', Account.number,
                      Account.settleDate,
                      Event.externalId,
                      setPerson.name AS setPerson,
                      Contract_Tariff.vat,
                      Event_LocalContract.coordDate,
                      Event_LocalContract.coordAgent,
                      Event_LocalContract.coordInspector,
                      if(rbPolicyType.code = 3,Insurer.shortName, coordOrg.shortName) AS coordOrg,
                      setOrgStructure.name AS setOrgStructure,
                      execOrgStructure.name AS execOrgStructure'''
        advancedFrom = ''' LEFT JOIN Contract_Tariff ON Contract_Tariff.id = Account_Item.tariff_id
                           LEFT JOIN vrbPersonWithSpeciality setPerson  ON setPerson.id = IF(Account_Item.visit_id IS NULL, IF(Account_Item.action_id IS NULL, Event.setPerson_id, Action.setPerson_id), Visit.person_id)
                           LEFT JOIN OrgStructure setOrgStructure ON setOrgStructure.id = setPerson.orgStructure_id
                           LEFT JOIN OrgStructure execOrgStructure ON execOrgStructure.id = execPerson.orgStructure_id
                           LEFT JOIN Event_LocalContract ON Event_LocalContract.master_id = Event.id AND Event_LocalContract.deleted = 0
                           LEFT JOIN Organisation coordOrg ON coordOrg.id = Event_LocalContract.org_id
                           LEFT JOIN Contract ON Contract.id = Account.contract_id'''
    else:
        advancedSelect = ''', ClientPolicy.serial    AS policySerial,
                              ClientPolicy.number    AS policyNumber,
                              Insurer.infisCode      AS policyInsurer'''
        advancedFrom = ''

    orderBy = '''Client.lastName,
                 Client.firstName,
                 Client.patrName,
                 Client.birthDate,
                 Account.number'''
    if groupType == 'SMO':
        orderBy = 'Insurer.shortName,' + orderBy
    
    #atronah(30.05.2012, 344): убрал из запроса "Account_Item.sum       AS sum" и добавил "Account_Item.price       AS price". 
    #сумма будет вычисляться как price*amount
    stmt="""
        SELECT
            Client.id,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.birthDate,
            Diagnosis.MKB AS MKB,
            (SELECT GROUP_CONCAT(Diagnosis.MKB) AS MKB
             FROM Diagnosis
                INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id
                INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
            WHERE
                Diagnostic.event_id = Account_Item.event_id
                AND Diagnostic.deleted = 0
                AND Diagnosis.deleted = 0
                AND rbDiagnosisType.code = '9') AS diagAccompMKB,
            IF(rbService.name IS NULL, EventType.name, rbService.name) AS service,
            IF(rbService.code IS NULL, '',             rbService.code) AS serviceCode,
            execPerson.name AS person,
            Event.execDate         AS eventDate,
            CONCAT(CreatePerson.lastName, ' ', CONCAT(CreatePerson.firstName, ' ', CreatePerson.patrName)) AS createPerson,
            Action.endDate         AS actionDate,
            assistant.name         AS assistant,
            Event.setDate          AS eventsetDate,
            Action.begDate         AS actionbegDate,
            Visit.date             AS visitDate,
            Account_Item.amount    AS amount,
            Account_Item.uet       AS uet,
            Account_Item.price     AS price,
            Event.modifyDateTime   AS modifyDateTime,
            CONCAT(Person.lastName, ' ', CONCAT(Person.firstName, ' ', Person.patrName)) AS modifyPerson,
            Insurer.id as insurer_id
            %(advancedSelect)s

        FROM
            Account_Item
            INNER JOIN Account      ON Account.id = Account_Item.master_id AND Account.deleted = 0
            LEFT JOIN Event         ON  Event.id  = Account_Item.event_id
            LEFT JOIN Person        ON  Person.id = Event.modifyPerson_id
            LEFT JOIN Person AS CreatePerson ON CreatePerson.id = Event.createPerson_id
            LEFT JOIN EventType     ON  EventType.id = Event.eventType_id
            LEFT JOIN Visit         ON  Visit.id  = Account_Item.visit_id
            LEFT JOIN Action        ON  Action.id  = Account_Item.action_id
            LEFT JOIN ActionType    ON  ActionType.id = Action.actionType_id
            LEFT JOIN Client        ON  Client.id = Event.client_id


            LEFT JOIN Diagnosis     ON Diagnosis.id = IF(Account_Item.visit_id IS NULL,
                                                         getEventDiagnosis(Account_Item.event_id),
                                                         getEventPersonDiagnosis(Account_Item.event_id, Visit.person_id))
            LEFT JOIN rbService ON rbService.id =
                IF(Account_Item.service_id IS NOT NULL,
                   Account_Item.service_id,
                   IF(Account_Item.visit_id IS NOT NULL, Visit.service_id, EventType.service_id)
                  )
            LEFT JOIN vrbPersonWithSpeciality execPerson ON execPerson.id = IF(Account_Item.visit_id IS NULL, IF(Account_Item.action_id IS NULL, Event.execPerson_id, Action.person_id), Visit.person_id)
            LEFT JOIN vrbPersonWithSpeciality assistant  ON assistant.id = IF(Account_Item.visit_id IS NULL,
                                                                                IF(Account_Item.action_id IS NULL,
                                                                                    Event.assistant_id,
                                                                                    (SELECT A_A.person_id
                                                                                     FROM Action_Assistant AS A_A
                                                                                        INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                                                                                     WHERE A_A.action_id = Account_Item.action_id AND rbAAT.code like 'assistant'
                                                                                     LIMIT 1)),
                                                                                Visit.assistant_id)
            LEFT JOIN Event MainEvent ON MainEvent.id = IFNULL(Action.event_id, IFNULL(Visit.event_id, Event.id))
            LEFT JOIN ClientPolicy ON ClientPolicy.id = MainEvent.clientPolicy_id
            LEFT JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            %(advancedFrom)s
        WHERE
            %(whereCond)s
        ORDER BY %(order)s""" % {'whereCond'     : db.joinAnd(cond),
                                      'advancedSelect': advancedSelect,
                                      'advancedFrom'  :  advancedFrom,
                                      'order': orderBy
                                }

    return db.query(stmt)

def buildReport():
    dialog = CAccount()
    dialog.setTitle(u'Сводный реестр услуг')
    if dialog.exec_():
        report = CAccountRegistry(None, True)
        params = dialog.params()
        financeDict = params.get('finance', None)
        financeList = financeDict.keys()
        reportTxt = report.build(u'типы финансирования: ' + ', '.join([forceString(financeDict[key]) for key in financeList]), params)
        view = CReportViewDialog()
        view.setWindowTitle(report.title())
        view.setText(reportTxt)
        view.setQueryText(report.queryText)
        view.setRepeatButtonVisible(True, buildReport)
        view.exec_()


class CAccountRegistry(CReportBase):
    def __init__(self, parent, report=False):
        CReportBase.__init__(self, parent)
        if report:
            self.setTitle(u'Сводный реестр услуг')
        else:
            self.setTitle(u'Реестр счёта')
        self.report = report

    def selectColumns(self, tableColumns):
        # обязательные колонки - №, ФИО, Кол-во, Сумма
        neededCols = [0, 1, 6, 13, 14]
        def getHiddenCols():
            ColsIndexes = set()
            for x in range(len(tableColumns)):
                ColsIndexes.add(x)

            visibleColsIndexes = set()
            for x in neededCols:
                visibleColsIndexes.add(x)

            for index in dialog.lstItems.selectedIndexes():
                visibleColsIndexes.add(tableColumns.index(forceString(index.data())))

            visibleColsIndexes = set(sorted(visibleColsIndexes))
            return visibleColsIndexes, ColsIndexes - visibleColsIndexes

        dialog = QtGui.QDialog()
        dialog.setWindowTitle(u'Выбор полей для печати')
        dialog.layout = QtGui.QVBoxLayout(dialog)
        dialog.lblDescription = QtGui.QLabel(
            u'Выберите поля для печати:\nОбязательные столбцы: №, ФИО, Профиль (услуга), Кол-во, Сумма',
            dialog
        )
        dialog.lstItems = QtGui.QListWidget(dialog)
        dialog.lstItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        viewCols = []
        for x in tableColumns:
            if tableColumns.index(x) not in neededCols:
                viewCols.append(x)

        dialog.lstItems.addItems(viewCols)
        dialog.lstItems.selectAll()
        dialog.buttonBox = QtGui.QDialogButtonBox(dialog)
        dialog.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok
        )
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        dialog.layout.addWidget(dialog.lblDescription)
        dialog.layout.addWidget(dialog.lstItems)
        dialog.layout.addWidget(dialog.buttonBox)
        hiddenColsIndexes = set()
        visibleColIndexes = set()
        if dialog.exec_():
            visibleColIndexes, hiddenColsIndexes = getHiddenCols()
        return visibleColIndexes, hiddenColsIndexes

    def build(self, description, params):
        def isVisibleCols(index):
            if hiddenColsIndexes:
                if index not in hiddenColsIndexes:
                    return True
                else:
                    return False
            else:
                return True

        hiddenColsIndexes = None
        financeId = params.get('currentFinanceId', None)
        accountItemIdList = params.get('accountItemIdList', None)
        orgInsurerId = params.get('orgInsurerId', None)
        chkAssistant    = params.get('assistant', False)
        groupType = params.get('groupType', 'client')
        if self.report:
            query = selectData(None, None, advanced=True, params=params)
        else:
            if orgInsurerId:
                self.setTitle(u'Реестр счета на СМО')
                query = selectData(accountItemIdList, financeId, orgInsurerId)
            else:
                query = selectData(accountItemIdList, financeId)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()
        
        format.setFontPointSize(8)
        format.setFontWeight(QtGui.QFont.Bold)
        cursor.setCharFormat(format)
        cursor.insertText(self.title())


        cursor.insertBlock()
        format.setFontWeight(QtGui.QFont.Normal)
        cursor.setCharFormat(format)
        cursor.insertText(description)
        
        cursor.insertBlock()
        additionalCol = 0
        tableColumns = [('26=', [u'№'                    ], CReportBase.AlignRight),
                        ('26?', [u'ФИО'                   ], CReportBase.AlignLeft),
                        ('9?',  [u'Код\nпрофиля\n(услуги)'], CReportBase.AlignLeft),
                        ('8?',  [u'Профиль\n(услуга)'     ], CReportBase.AlignLeft),
                        ('8?',  [u'Начато'                ], CReportBase.AlignLeft),
                        ('8?',  [u'Закончено'             ], CReportBase.AlignLeft),
                        ('8?',  [u'Автор создания обращения'], CReportBase.AlignLeft),
                        ('8?',  [u'Дата закрытия карточки/Сотрудник'], CReportBase.AlignLeft),
                        ('7?',  [u'Тариф'                 ], CReportBase.AlignRight),
                        ('7?',  [u'Кол-\nво'              ], CReportBase.AlignRight),
                        ('7?',  [u'Сумма'                 ], CReportBase.AlignRight)]

        lenDif = 0
        visibleCols = dict()
        if self.report:
            tableColumns.insert(1, ('8?', [u'Номер\nреестра'                               ], CReportBase.AlignLeft))
            tableColumns.insert(2, ('8?', [u'Дата\nреестра'                                ], CReportBase.AlignLeft))
            tableColumns.insert(4, ('8?', [u'Номер\nмедицинской\nкарты'                    ], CReportBase.AlignLeft))
            tableColumns.append(('8?', [u'В том числе',       u'НДС'                       ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'',                  u'Сумма\nбез НДС'            ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'Оказание услуги',   u'Структурное\nподразделение'], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'',                  u'ФИО\nисполнителя'          ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'Назначение услуги', u'Структурное\nподразделение'], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'',                  u'ФИО\nисполнителя'          ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'Заказчик'                                        ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'Согласование',      u'ФИО\nзаказчика'            ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'',                  u'ФИО\nисполнителя'          ], CReportBase.AlignCenter))
            tableColumns.append(('8?', [u'',                  u'Дата'                      ], CReportBase.AlignCenter))
            additionalCol -= 1

            count = 0
            for x in range(23):
                visibleCols[str(x)] = count
                count += 1
        else:
            tableColumns.insert(2, ('6?',  [u'Дата\nрождения'], CReportBase.AlignLeft))
            tableColumns.insert(3, ('7?',  [u'Полис'         ], CReportBase.AlignCenter))
            tableColumns.insert(4, ('7?',  [u'Ди-\nаг-\nноз' ], CReportBase.AlignLeft))
            tableColumns.insert(7, ('20?', [u'Врач'          ], CReportBase.AlignLeft))

            columns = [
                u'№',
                u'ФИО',
                u'Дата рождения',
                u'Полис',
                u'Диагноз',
                u'Код профиля (услуги)',
                u'Профиль (услуга)',
                u'Врач',
                u'Начато',
                u'Закончено',
                u'Автор создания обращения'
                u'Дата закрытия карточки/Сотрудник',
                u'Тариф',
                u'Кол-во',
                u'Сумма'
            ]
            if chkAssistant:
                tableColumns.insert(8, ('20?', [u'Ассистент'], CReportBase.AlignLeft))
                columns.insert(8, u'Ассистент')
                additionalCol = 1

            visibleColIndexes, hiddenColsIndexes = self.selectColumns(columns)
            hiddenCols = []
            for i in range(len(tableColumns)):
                if i in hiddenColsIndexes:
                    hiddenCols.append(tableColumns[i])
            for x in hiddenCols:
                tableColumns.remove(x)
            visibleCols = dict()
            count = 0
            for x in visibleColIndexes:
                visibleCols[str(x)] = count
                count += 1

            lenDif = len(columns) - len(visibleCols)# - 2
            if not len(hiddenColsIndexes):
                lenDif = 0

        format.setFontWeight(QtGui.QFont.Bold)
        table = createTable(cursor, tableColumns,  charFormat=format)
        format.setFontWeight(QtGui.QFont.Normal)
        if self.report:
            for column in xrange(12):
                table.mergeCells(0, column, 2, 1)
            table.mergeCells(0, 12, 1, 2)
            table.mergeCells(0, 14, 1, 2)
            table.mergeCells(0, 16, 1, 2)
            table.mergeCells(0, 18, 2, 1)
            table.mergeCells(0, 19, 1, 3)

        totalAmount = 0

        totalSum    = 0.0
        n = 0
        prevClientId = -1
        totalClientSum = 0.0
        totalClientAmount = 0
        self.queryText = forceString(query.lastQuery())

        def formatRow(record, n, amount, price, sum):
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            service = forceString(record.value('service'))
            serviceCode = forceString(record.value('serviceCode'))
            person = forceString(record.value('person'))
            dateassign = forceDate(record.value('actionbegDate'))
            if dateassign.isNull():
                dateassign = forceDate(record.value('visitDate'))
            if dateassign.isNull():
                dateassign = forceDate(record.value('eventsetDate'))
            date = forceDate(record.value('actionDate'))

            if date.isNull():
                date = forceDate(record.value('visitDate'))
            if date.isNull():
                date = forceDate(record.value('eventDate'))

            if self.report:
                vat = sum * forceDouble(record.value('vat'))
                result = [n,
                          forceString(record.value('number')),
                          forceDate(record.value('settleDate')).toString('dd.MM.yyyy'),
                          name,
                          forceString(record.value('externalId')),
                          serviceCode,
                          service,
                          forceString(dateassign),
                          forceString(date),
                          forceString(record.value('createPerson')),
                          forceDate(record.value('modifyDateTime')).toString('dd.MM.yyyy') + '/' + forceString(record.value('modifyPerson')),

                          price,
                          amount,
                          sum,
                          vat,
                          sum - vat,
                          forceString(record.value('execOrgStructure')),
                          person,
                          forceString(record.value('setOrgStructure')),
                          forceString(record.value('setPerson')),
                          forceString(record.value('coordOrg')),
                          forceString(record.value('coordInspector')),
                          forceString(record.value('coordAgent')),
                          forceDate(record.value('coordDate')).toString('dd.MM.yyyy')]
            else:
                diagAccompMKB = forceString(record.value('diagAccompMKB'))
                result = [n,
                          name,
                          forceString(record.value('birthDate')),
                          ' '.join([forceString(record.value('policySerial')), forceString(record.value('policyNumber')), forceString(record.value('policyInsurer'))]),
                          ', '.join([forceString(record.value('MKB')), diagAccompMKB]) if diagAccompMKB else forceString(record.value('MKB')),
                          serviceCode,
                          service,
                          person,
                          forceString(dateassign),
                          forceString(date),
                          forceString(record.value('createPerson')),
                          forceDate(record.value('modifyDateTime')).toString('dd.MM.yyyy') + '/' + forceString(record.value('modifyPerson')),


                          price,
                          amount,
                          sum]
                if chkAssistant:
                    result.insert(8, forceString(record.value('assistant')))
            return result

        grandTotalAmount = 0
        grandTotalSum = 0
        while query.next():
            n += 1
            record = query.record()
            if groupType == 'client':
                clientId = forceRef(record.value('id'))
            else:
                clientId = forceRef(record.value('insurer_id'))
            amount = forceInt(record.value('amount'))
            price   = forceDouble(record.value('price'))
            sum = price * amount

            if clientId == prevClientId or prevClientId == -1:
                totalClientAmount += amount
                totalClientSum += sum
            elif prevClientId != -1:
                i = table.addRow()
                table.mergeCells(i, 1, 1, 9 - lenDif if self.report else 10 - lenDif)
                format.setFontWeight(QtGui.QFont.Bold)
                if groupType == 'client':
                    table.setText(i,  1, u'Итого по клиенту:', format, CReportBase.AlignLeft)
                else:
                    table.setText(i,  1, u'Итого по компании:', format, CReportBase.AlignLeft)
                if visibleCols.has_key(str(13)):
                    table.setText(i, visibleCols[str(13 + additionalCol)], totalClientAmount, format)
                    grandTotalAmount += totalClientAmount
                if visibleCols.has_key(str(14)):
                    table.setText(i, visibleCols[str(14 + additionalCol)], QtCore.QString.number(totalClientSum, 'g', 9), format)
                    grandTotalSum += totalClientSum
                #table.setText(i, 11 + additionalCol, totalClientAmount, format)
                #table.setText(i, 13 + additionalCol, QtCore.QString.number(totalClientSum, 'g', 9), format)
                if self.report:
                    table.mergeCells(i, 14, 1, 13)
                format.setFontWeight(QtGui.QFont.Normal)
                totalClientAmount = amount
                totalClientSum = sum
            prevClientId = clientId

            i = table.addRow()
            for col, value in enumerate(formatRow(record, n, amount, price, sum)):
                if visibleCols.has_key(str(col)):
                    table.setText(i, visibleCols[str(col)], value)

            totalAmount += amount
            totalSum += sum
        
        i = table.addRow()
        table.mergeCells(i, 1, 1, 9 - lenDif if self.report else 11 - lenDif)
        format.setFontWeight(QtGui.QFont.Bold)
        if groupType == 'client':
            table.setText(i,  1, u'Итого по клиенту:', format, CReportBase.AlignLeft)
        else:
            table.setText(i,  1, u'Итого по компании:', format, CReportBase.AlignLeft)
        if visibleCols.has_key(str(12)):
            table.setText(i, visibleCols[str(13 + additionalCol)], totalClientAmount, format)
            grandTotalAmount += totalClientAmount
        if visibleCols.has_key(str(13)):
            table.setText(i, visibleCols[str(14 + additionalCol)], QtCore.QString.number(totalClientSum, 'g', 9),
                          format)
            grandTotalSum += totalClientSum
        #table.setText(i, 11 + additionalCol, totalClientAmount, format)
        #table.setText(i, 13 + additionalCol, QtCore.QString.number(totalClientSum, 'g', 9), format)
        if self.report:
            table.mergeCells(i, 14, 1, 13)
        format.setFontWeight(0)

        i = table.addRow()

        table.mergeCells(i, 0, 1, 12 - lenDif if self.report else 12 - lenDif)
        format.setFontWeight(QtGui.QFont.Bold)
        table.setText(i,  0, u'Итого',   format, CReportBase.AlignLeft)
        if visibleCols.has_key(str(12)):
            table.setText(i, visibleCols[str(13 + additionalCol)], grandTotalAmount, format)
            # table.setText(i, visibleCols[str(12 + additionalCol)], totalClientAmount, format)
        if visibleCols.has_key(str(13)):
            table.setText(i, visibleCols[str(14 + additionalCol)], QtCore.QString.number(grandTotalSum, 'g', 9), format)
            # table.setText(i, visibleCols[str(13 + additionalCol)], QtCore.QString.number(totalClientSum, 'g', 9), format)
        #table.setText(i, 11 + additionalCol, totalAmount, format)
        #table.setText(i, 13 + additionalCol, QtCore.QString.number(totalSum, 'g', 9), format)
        if self.report:
            table.mergeCells(i, 13, 1, 12)
        format.setFontWeight(QtGui.QFont.Normal)
        cursor.movePosition(cursor.End)
        cursor.insertBlock(CReportBase.AlignRight)
        createAutographField(cursor, [u'Гл. врач', u'Гл. бухгалтер'], getOrganisationMainStaff(QtGui.qApp.currentOrgId()), format, isAddSignatureField = False)                    
        return doc





class CLocInsurerForm(QtGui.QWidget, Ui_Form):
    __pyqtSignals__ = ('insurerChanged(QWidget *, int)',
                       )

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.chkWithout.setEnabled(False)
        self.connect(self.cmbInsurer, QtCore.SIGNAL('currentIndexChanged(int)'), self.onInsurerChanged)

        self.oldValue = None

    @QtCore.pyqtSlot(int)
    def onInsurerChanged(self, index):
        newValue = self.cmbInsurer.value()
        if newValue != self.oldValue:
            self.chkWithout.setEnabled(not newValue is None)
            self.oldValue = newValue
            self.emit(QtCore.SIGNAL('insurerChanged(QWidget *, int)'), self, forceInt(newValue))

    def value(self):
        return self.cmbInsurer.value(), self.chkWithout.isChecked()

    def isChecked(self):
        return self.chkWithout.isChecked()

    def insurerId(self):
        return self.cmbInsurer.value()


class CAccount(QtGui.QDialog, Ui_ReportAccount):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstItems.setTable('rbFinance')
        self.addInsurerForm()

    @QtCore.pyqtSlot(int, int)
    def onInsurerChanged(self, insurerForm, value):
        layoutSize = self.verticalLayout.count()
        lastInsurer = self.verticalLayout.itemAt(layoutSize-1).widget()
        if insurerForm == lastInsurer and value:
            self.addInsurerForm()
        elif layoutSize > 1 and not value:
            if len(filter(lambda v: v is None, self.insurerIdList())) > 1:
                self.removeEmptyInsurerForm(insurerForm)

    def insurerIdList(self):
        layoutSize = self.verticalLayout.count()
        return map(lambda w: w.insurerId(), filter(lambda w: isinstance(w, CLocInsurerForm), [self.verticalLayout.itemAt(idx).widget() for idx in xrange(layoutSize)]))

    def insurerList(self):
        layoutSize = self.verticalLayout.count()
        insurerForms = filter(lambda w: isinstance(w, CLocInsurerForm) and not w.insurerId() is None, [self.verticalLayout.itemAt(idx).widget() for idx in xrange(layoutSize)])
        return [f.insurerId() for f in insurerForms if not f.isChecked()], [f.insurerId() for f in insurerForms if f.isChecked()]

    def addInsurerForm(self):
        insurerForm = CLocInsurerForm(self.verticalLayout)
        QtCore.QObject.connect(insurerForm, QtCore.SIGNAL('insurerChanged(QWidget *, int)'), self.onInsurerChanged)
        self.verticalLayout.addWidget(insurerForm)

    def removeEmptyInsurerForm(self, insurerForm):
        QtCore.QObject.disconnect(insurerForm.cmbInsurer, QtCore.SIGNAL('currentIndexChanged(int)'), insurerForm.onInsurerChanged)
        QtCore.QObject.disconnect(insurerForm, QtCore.SIGNAL('insurerChanged(QWidget *, int)'), self.onInsurerChanged)
        self.verticalLayout.removeWidget(insurerForm)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbInsurer.setValue(params.get('orgInsurerId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['finance'] = self.lstItems.nameValues()
        result['insurerList'] = self.insurerList()
        result['dateType'] = 'account' if self.rbtnAccountDate.isChecked() else 'service'
        result['groupType'] = 'client' if self.rbtnClient.isChecked() else 'SMO'
        return result


# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     connectionInfo = {
#         'driverName': 'mysql',
#         'host': 'pacs',
#         'port': 3306,
#         'database': 's11vm',
#         'user': 'dbuser',
#         'password': 'dbpassword',
#         'connectionName': 'vista-med',
#         'compressData': True,
#         'afterConnectFunc': None
#     }
#     QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
#
#     w = CAccountRegistry(None)
#     w.exec_()
#
#
# if __name__ == '__main__':
#     main()
