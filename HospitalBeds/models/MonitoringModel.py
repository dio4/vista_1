# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Utils import getRealPayed
from HospitalBeds.HospitalizationEventDialog import getActionTypeIdListByFlatCode
from HospitalBeds.Utils import getAgeRangeCond, getStatusObservation, getEventFeedId, \
    getCurrentOSHB, getCurrentOSHBProfile, getDataOrgStructureName, \
    getDataClientQuoting, getQuotingTypeIdList, \
    getDataAPHB
from Registry.Utils import getStaffCondition
from library.TableModel import CCol
from library.Utils import smartDict, toVariant, getMKB, getProvisionalDiagnosis, \
    getAdmissionDiagnosis, getDataOSHB, getDataOSHBProfile, \
    forceInt, forceDateTime, forceString, forceDate, calcAge, \
    calcAgeInYears, forceBool, forceRef, forceStringEx, \
    formatSNILS


# Присутствуют - Список - 1
class CMonitoringCol(CCol):
    ## Конструктор столбца
    # @param title: полное имя столбца (выводится в подсказке при наведении мыши)
    # @param fields: список имен полей, данные которых необходимы для столбца.
    # @param defaultWidth: ширина столбца по умолчанию (целое число).
    # @param alignment: выравнивание данных в столбце. Допустимые значения: CCol.alg.keys()  ('l', 'c', 'r', ')
    # @param shortTitle: сокращенное имя столбца, выводится в шапку таблицы.
    # @param displayFieldNumber: индекс поля из fields, данные которого выводятся в столбце для Qt.DisplayRole
    # @param otherRolesInfo: справочник с информацией о полях, из которые требуется брать данные для той или иной пользовательской роли (>= Qt.UserRole)
    #                        Данные вида {<role> : 'fieldName'}
    def __init__(self, title, fields, defaultWidth, alignment, shortTitle=None, displayFieldNumber=0, otherRolesInfo=None):
        if not otherRolesInfo:
            otherRolesInfo = {}
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        self._shortTitle = shortTitle if shortTitle else title
        self._displayFieldNumber = displayFieldNumber
        self._otherRolesInfo = otherRolesInfo

    def title(self, short = False):
        if short:
            return self._shortTitle
        return CCol.title(self)

    def setTitle(self, title, short = False):
        if short:
            self._shortTitle = title
        else:
            CCol.setTitle(self, title)

    def displayFieldNumber(self):
        return self._displayFieldNumber

    def setDisplayFieldNumber(self, number):
        if 0 < number < len(self.fields()):
            self._displayFieldNumber = number

    def otherRolesInfo(self):
        return self._otherRolesInfo


class CMonitoringModel(QtCore.QAbstractTableModel):
    sex = [u'', u'М', u'Ж']
    vipClientColor = QtGui.QColor(255, 215, 0)  # u'cyan'

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.headerSortingCol = {}
        self._cols = []
        self.mapColFieldNameToColIndex = {}
        self.tables = smartDict()
        self.initTables()
        self._columnNamesList = []

    def initTables(self):
        db = QtGui.qApp.db
        self.tables.Action = db.table('Action')
        self.tables.ActionType = db.table('ActionType')
        self.tables.Event = db.table('Event')
        self.tables.EventType = db.table('EventType')
        self.tables.Client = db.table('Client')
        self.tables.ClientAttach = db.table('ClientAttach')
        self.tables.RBAttachType = db.table('rbAttachType')
        self.tables.PWS = db.table('vrbPersonWithSpeciality')
        self.tables.APT = db.table('ActionPropertyType')
        self.tables.APOS = db.table('ActionProperty_OrgStructure')
        self.tables.AP = db.table('ActionProperty')
        self.tables.APS = db.table('ActionProperty_String')
        self.tables.APHB = db.table('ActionProperty_HospitalBed')
        self.tables.OS = db.table('OrgStructure')
        self.tables.OSHB = db.table('OrgStructure_HospitalBed')
        self.tables.Contract = db.table('Contract')
        self.tables.OrdAP = db.table('ActionProperty').alias('OrdActionProperty')
        self.tables.OrdAPS = db.table('ActionProperty_String').alias('OrdActionProperty_String')
        self.tables.OrdAPT = db.table('ActionPropertyType').alias('OrdActionPropertyType')
        self.tables.Quota = db.table('QuotaType')
        self.tables.LocationCard = db.table('Event_HospitalBedsLocationCard')

    def cols(self):
        return self._cols

    def getColumnByFieldName(self, fieldName):
        if fieldName not in self.mapColFieldNameToColIndex:
            for i, column in enumerate(self.cols()):
                fields = column.fields()
                for field in fields:
                    if field not in self.mapColFieldNameToColIndex:
                        self.mapColFieldNameToColIndex[field] = i
        index = self.mapColFieldNameToColIndex.get(fieldName, None)
        return self.cols()[index]

    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self._cols)

    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self._cols[section].title(short = True))
            elif role == QtCore.Qt.ToolTipRole:
                return QtCore.QVariant(self._cols[section].title(short = False))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        # Получение данных о пользовательских ролях данных
        columnOtherRolesInfo = column.otherRolesInfo()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            displayFieldNumber = column.displayFieldNumber()
            return toVariant(item.get(columnFieldNames[displayFieldNumber], QtCore.QVariant()))
        elif role == QtCore.Qt.ToolTipRole:
            result = []
            item = self.items[row]
            for fieldName in columnFieldNames:
                value = item.get(fieldName, '')
                if isinstance(value, basestring):
                    result.append(value)
            return toVariant(' '.join(result))
        # если роль совпадает с одной из настроенных пользвовательских ролей для столбца
        elif columnOtherRolesInfo.has_key(role):
            # получение имени поля, данные из которого необходимо вернуть для данной роли
            userRoleFieldName = columnOtherRolesInfo[role]
            item = self.items[row]
            return toVariant(item.get(userRoleFieldName, QtCore.QVariant()))
        return QtCore.QVariant()

    ## Сформировать столбцы с данными по финансированию в параметрах запроса (таблица, условие, список полей)
    #    @param cols: список полей запроса, куда будут добавлены (в конец) 2 поля по финансированию.
    #    @param cond: список условий для добавление в него проверок, связанных с финансированием.
    #    @param queryTable: таблица(CTable, CJoin), к которой необходимо приджойнить необходимые таблицы.
    #    @param financeId: фильтр типов финансирования.
    @staticmethod
    def compileFinanceCols(cols, cond, queryTable, financeId = None, excludeByActionMode = False):
        db = QtGui.qApp.db
        tableRBFinance = db.table('rbFinance')
        tableRBFinanceByContract = db.table('rbFinance').alias('rbFinanceByContract')
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableContract = db.table('Contract')

        financeMode = QtGui.qApp.defaultHospitalBedFinanceByMoving() #(global preference with code = 9)

        financeCond = []
        financeCol = None

        # джойним таблицу Contract и 3 ее поля, необходимых для формирования колонки "Договор" (Д)
        joinCond = [tableContract['id'].eq(tableEvent['contract_id']),
                    tableContract['deleted'].eq(0)]
        if financeId:
            queryTable = queryTable.innerJoin(tableContract, joinCond)
        else:
            queryTable = queryTable.leftJoin(tableContract, joinCond)
        cols.extend([tableContract['number'].alias('contract_number'),
                     tableContract['date'].alias('contract_date'),
                     tableContract['resolution'].alias('contract_resolution')])

        # Джойн типа финансирования по действию
        if financeMode != 0 and not excludeByActionMode: #atronah: not only by Event
            # В качестве (кода, имени) финансирования использовать данные о финансировании из движения
            financeCol = (tableRBFinance['code'].name(),
                          tableRBFinance['name'].name())
            if financeId:
                queryTable = queryTable.innerJoin(tableRBFinance, tableRBFinance['id'].eq(tableAction['finance_id']))
                financeCond.append(tableRBFinance['id'].eq(financeId))
            else:
                queryTable = queryTable.leftJoin(tableRBFinance, tableRBFinance['id'].eq(tableAction['finance_id']))

        # Джойн типа финансирования по договору события
        if financeMode != 1: #atronah: not only by Action
            if financeCol is None: # Если (код, имя) финансирования еще не заданы (будет только в случае, когда financeMode == 0, т.е. "по событию"
                # То в качестве (кода, имени) финансирования использовать данные о финансировании из события
                financeCol = (tableRBFinanceByContract['code'].name(),
                              tableRBFinanceByContract['name'].name())
            else: # иначе (в случае, когда financeMode == 2, т.е. "по движению или по событию")
                # то в качестве (кода, имени) финансирования использовать данные из движения, если они имеются, иначе использовать данные из события
                ifTemplate = 'IF(%s IS NOT NULL, %s, %s)'
                financeCol = (ifTemplate % (financeCol[0], financeCol[0], tableRBFinanceByContract['name'].name()),
                              ifTemplate % (financeCol[1], financeCol[1], tableRBFinanceByContract['name'].name()))

            if financeId:
                queryTable = queryTable.innerJoin(tableRBFinanceByContract, tableRBFinanceByContract['id'].eq(tableContract['finance_id']))
                financeCond.append(tableRBFinanceByContract['id'].eq(financeId))
            else:
                queryTable = queryTable.leftJoin(tableRBFinanceByContract, tableRBFinanceByContract['id'].eq(tableContract['finance_id']))

        if financeCond:
            cond.append(db.joinOr(financeCond))
        cols.append('%s AS codeFinance' % financeCol[0])
        cols.append('%s AS nameFinance' % financeCol[1])

        return queryTable

    def compileCommonFilter(self, params, queryTable, cond, actionPerson = False):
        """
         Формирование условий по фильтрам в группе "Пациент"
        """
        accountingSystemId = params.get('accountingSystemId', None)
        clientId = params.get('clientId', None)
        eventId = params.get('eventId', None)
        statusObservation = params.get('statusObservation', None)
        personId = params.get('personId', None)
        indexSex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        # Система учёта
        if accountingSystemId and clientId:
            tableIdentification = QtGui.qApp.db.table('ClientIdentification')
            queryTable = queryTable.innerJoin(tableIdentification, tableIdentification['client_id'].eq(self.tables.Client['id']))
            cond.append(tableIdentification['accountingSystem_id'].eq(accountingSystemId))
            cond.append(tableIdentification['identifier'].eq(clientId))
            cond.append(tableIdentification['deleted'].eq(0))
        # По умолчанию - Виста-Мед
        elif clientId:
            cond.append(self.tables.Client['id'].eq(clientId))
        # Карта
        if eventId:
            cond.append(self.tables.Event['externalId'].eq(eventId))
        # Статус наблюдения
        if statusObservation:
            tableStatusObservation = QtGui.qApp.db.table('Client_StatusObservation')
            queryTable = queryTable.innerJoin(tableStatusObservation, tableStatusObservation['master_id'].eq(self.tables.Client['id']))
            cond.append(tableStatusObservation['deleted'].eq(0))
            cond.append(tableStatusObservation['statusObservationType_id'].eq(statusObservation))
        if personId:
            cond.append(self.tables.Event['execPerson_id'].eq(personId) if not actionPerson else self.tables.Action['person_id'].eq(personId))
        if indexSex > 0:
            cond.append(self.tables.Client['sex'].eq(indexSex))
        if ageFrom <= ageTo:
            cond.append(getAgeRangeCond(ageFrom, ageTo))
        if not QtGui.qApp.isDisplayStaff():
            cond.append('NOT (%s)' % getStaffCondition(self.tables.Client['id'].name()))
        return queryTable, cond

    def formColumnsList(self, tab):
        """tab:     1 - CPresenceModel / Присутствуют-Список-1
                    2 - CReceivedModel / Поступили
                    3 - CTransferModel / Переведены (в отделение)
                    4 - CLeavedModel / Выбыли
                    5 - CReadyToLeaveModel / Готовы к выбытию
                    6 - CQueueModel / В очереди
                    7 - CRenunciationModel / Отказ от госпитализации
                    8 - CDeathModel / Умерло
                    9 - CReanimationModel / Реанимация
                    10 - CLobbyModel / Приёмное отделение
                    11 - MaternitywardModel / Родовое отделение
            В CLobbyModel сейчас столбцы инициализируются в собственном конструкторе, данная функция не используется
        """
        self._cols = []
        if tab == 6:
            self._cols.append(CMonitoringCol(u'Дата назначения', ['begDate'], 20, 'l'))
        self._cols.append(CMonitoringCol(u'Статус наблюдения',     ['statusObservationCode', 'statusObservationName'], 20, 'l', shortTitle = u'С'))
        if tab == 4:
            self._cols.append(CMonitoringCol(u'Место нахождения истории болезни', ['locationCardName'], 30, 'l', shortTitle = u'И/Б'))
        self._cols.append(CMonitoringCol(u'Код ИФ',                ['codeFinance', 'nameFinance'], 20, 'l', shortTitle = u'И', displayFieldNumber = 1))
        if tab in (1, 2, 3, 4, 5, 6, 7, 8, 9):
            self._cols.append(CMonitoringCol(u'Договор',       ['contractInfo'], 20, 'l', shortTitle = u'Д'))
        if tab in (1, 2, 3, 4, 5, 9):
            self._cols.append(CMonitoringCol(u'Питание',               ['feed'], 20, 'l', shortTitle = u'П'))
        if tab == 1:
            self._cols.append(CMonitoringCol(u'Режим физической активности', ['physicalActivityName'], 20, 'l', shortTitle = u'Р'))
            self._cols.append(CMonitoringCol(u'Комфортность',          ['comfortableDate'], 20, 'l', shortTitle = u'К'))
        self._cols.append(CMonitoringCol(u'Номер',                 ['clientId'], 20, 'l'))
        self._cols.append(CMonitoringCol(u'Карта',                 ['externalId'], 20, 'l'))
        self._cols.append(CMonitoringCol(u'ФИО',                   ['clientName'], 30, 'l'))
        self._cols.append(CMonitoringCol(u'Пол',                   ['sex'], 15, 'l'))
        self._cols.append(CMonitoringCol(u'Дата рождения',         ['birthDate'], 20, 'l'))
        self._cols.append(CMonitoringCol(u'Возраст',               ['age'], 20, 'l'))
        self._cols.append(CMonitoringCol(u'СНИЛС',                 ['snils'], 20, 'l'))
        self._cols.append(CMonitoringCol(u'Трудоспособный возраст',['employable'], 20, 'l'))
        if tab == 6:
            self._cols.append(CMonitoringCol(u'Дата ГК',               ['directionDate'], 20, 'l'))
            self._cols.append(CMonitoringCol(u'Плановая дата госпитализации', ['plannedEndDate'], 20, 'l'))
            self._cols.append(CMonitoringCol(u'Ожидание',              ['waitingDays'], 20, 'l'))
        if tab in (2, 3, 4, 5, 8):
            self._cols.append(CMonitoringCol(u'Госпитализирован',      ['begDateReceived'], 20, 'l'))
        if tab in (1, 2, 3, 4, 5, 7):
            self._cols.append(CMonitoringCol(u'Поступил',              ['begDateString'], 20, 'l'))
        if tab in (2, 3, 4, 7, 8):
            self._cols.append(CMonitoringCol(u'Выбыл',                 ['endDate'], 20, 'l'))
        if tab == 7:
            self._cols.append(CMonitoringCol(u'Причина отказа',        ['nameRenunciate'], 20, 'l'))
        if tab in (1, 5):
            self._cols.append(CMonitoringCol(u'Плановая дата выбытия', ['plannedEndDate'], 20, 'l'))
        if tab in (1, 2, 3, 4, 5, 6, 7, 8):
            self._cols.append(CMonitoringCol(u'МКБ',                   ['MKB'], 20, 'l'))
        if tab in (1, 2):
            self._cols.append(CMonitoringCol(u'Предварительный диагноз', ['provisionalDiagnosis'], 20, 'l'))
            self._cols.append(CMonitoringCol(u'Диагноз приёмного отделения', ['admissionDiagnosis'], 20, 'l'))
        if tab in (1, 2, 3, 4, 5, 7, 8):
            self._cols.append(CMonitoringCol(u'Койка',                 ['codeBed', 'nameBed'], 30, 'l'))
        if tab in (1, 2, 3, 4):
            self._cols.append(CMonitoringCol(u'Профиль койки',          ['profileBed'], 30, 'l'))
        if tab == 9:
            self._cols.append(CMonitoringCol(u'Реанимирован',          ['begDateString'], 20, 'l'))

        self._cols.append(CMonitoringCol(u'Подразделение',         ['nameOS'], 30, 'l'))
        self._cols.append(CMonitoringCol(u'Код подразделения',         ['codeOS'], 30, 'l'))
        if tab in (3, 9):
            self._cols.append(CMonitoringCol(u'Переведен из',          ['nameFromOS'], 30, 'l'))
        if tab == 9:
            self._cols.append(CMonitoringCol(u'Числится за',          ['currentCommonOSName'], 30, 'l'))
        if tab in (1, 2, 3, 4, 5, 6, 7, 8):
            self._cols.append(CMonitoringCol(u'Ответственный',         ['namePerson'], 30, 'l'))
        if tab in (1, 2, 3):
            self._cols.append(CMonitoringCol(u'Уход',                  ['patronage'], 30, 'l'))
        # if tab in (2, 4):
        self._cols.append(CMonitoringCol(u'Квота', ['quota'], 30, 'l'))

    def getQueryCols(self, MKB=False, statusObservation=False, dateFeedFlag=False, OSHB=False, OSHBProfile=False,
                     nameOS=False, orgStructurePropertyNameList=None, currentOSHB=False, PWS=True, eventEndDate=False,
                     eventBegDate=False, patronage=False, provisionalDiagnosis=False, admissionDiagnosis=False,
                     params=None, order=False):
        if not params:
            params = {}
        db = QtGui.qApp.db
        cols = []
        cols.append(self.tables.Action['id'].alias('actionId'))
        cols.append(self.tables.Event['id'].alias('eventId'))
        cols.append(self.tables.Event['client_id'])
        cols.append(self.tables.Event['externalId'])
        cols.append(self.tables.Client['lastName'])
        cols.append(self.tables.Client['firstName'])
        cols.append(self.tables.Client['patrName'])
        cols.append(self.tables.Client['sex'])
        cols.append(self.tables.Client['birthDate'])
        cols.append(self.tables.Client['SNILS'])
        cols.append(self.tables.Action['begDate'] if not eventBegDate else self.tables.Event['setDate'].alias('begDate'))
        cols.append(self.tables.Action['endDate'] if not eventEndDate else self.tables.Event['execDate'].alias('endDate'))
        cols.append(self.tables.Event['setDate'])
        cols.append(self.tables.Action['plannedEndDate'])
        cols.append(self.tables.Action['actionType_id'])
        cols.append(self.tables.Action['finance_id'])
        cols.append(self.tables.Event['contract_id'])
        cols.append(self.tables.Event['result_id'])
        cols.append(self.tables.Action['directionDate'])
        if u'онко' in forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')):
            cols.append('IF(EXISTS(SELECT * FROM ClientVIP WHERE ClientVIP.deleted = 0 AND ClientVIP.client_id = Client.id), 1, 0) AS isVIP')
            cols.append('(SELECT color FROM ClientVIP WHERE ClientVIP.deleted = 0 AND ClientVIP.client_id = Client.id) AS vipColor')

        if order:
            cols.append(self.tables.OrdAPS['value'].alias('ordChannel'))
            cols.append(self.tables.Event['order'].alias('ordType'))

        if PWS:
            cols.append(self.tables.PWS['name'].alias('namePerson'))
            cols.append(self.tables.PWS['id'].alias('personId'))

        if MKB:
            cols.append(getMKB())
        if provisionalDiagnosis:
            cols.append(getProvisionalDiagnosis())
        if admissionDiagnosis:
            cols.append(getAdmissionDiagnosis())
        if statusObservation:
            cols.append(getStatusObservation())
        if dateFeedFlag:
            dateFeed = params.get('dateFeed', QtCore.QDate.currentDate())
            if not dateFeed:
                dateFeed = QtCore.QDate.currentDate()
            cols.append(getEventFeedId(db.formatDate(dateFeed), u''' AS countEventFeedId'''))
        # Загрузка имен коек и профилей коек как-то ни разу не эффективна, но джойнить эти 5-7 табличек не красиво.
        if OSHB:
            cols.append(getDataOSHB())
            if OSHBProfile:
                cols.append(getDataOSHBProfile())

        if currentOSHB:
            cols.append(getCurrentOSHB())
            if OSHBProfile:
                cols.append(getCurrentOSHBProfile())
        if patronage:
            col = u'''EXISTS(SELECT APS.id
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
    WHERE  Action.id IS NOT NULL AND APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND (APT.name LIKE 'Уход' OR APT.name LIKE 'Патронаж') AND APS.value = 'да') as patronage'''
            cols.append(col)

        # Добавление столбца с именем подразделения
        # либо на основании имени свойства действия (непустое orgStructurePropertyNameList),
        # либо на основании присоединенной таблицы подразделений (nameOS == True)
        if orgStructurePropertyNameList:
            cols.append(getDataOrgStructureName(orgStructurePropertyNameList))
        elif nameOS: #FIXME: atronah: возможно if стоит переделать на elif, так как при bool(nameProperty) == True уже добавляется столбец с именем nameOS
            cols.append(u'IF(OrgStructure.id IS NOT NULL AND OrgStructure.deleted=0, OrgStructure.name, NULL) AS nameOS, '
                        u'IF(OrgStructure.id IS NOT NULL AND OrgStructure.deleted=0, OrgStructure.code, NULL) AS codeOS')

        cols.append(u'Client.isUnconscious')
        # cols.append(u'Client.isVIP')
        return cols

    ## Формирует общую таблицу (группу джойнов для секции FROM запроса) и условия (для секции WHERE запроса)
    # @param flatCodeCond: flatCode типа действия, для которого делается выборка ('received%' - поступление, 'moving%' - движение, 'leaved%' - выписка и т.п.).
    # @param AT: задает необходимость присоединения таблицы ActionType. True - присоединять (INNER JOIN), False - не присоединять.
    # @param APT: задаест способ присоединения таблицы ActionPropertyType. 0 - не присоединять, 1 - присоединять жестко (INNER JOIN), 2 - присоединять мягко (LEFT JOIN).
    # @param AP: задаест способ присоединения таблицы ActionProperty. 0 - не присоединять, 1 - присоединять жестко (INNER JOIN), 2 - присоединять мягко (LEFT JOIN).
    # @param APOS: задаест способ присоединения таблицы ActionProperty_OrgStructure. 0 - не присоединять, 1 - присоединять жестко (INNER JOIN), 2 - присоединять мягко (LEFT JOIN).
    # @param OS: задаест способ присоединения таблицы OrgStructure. 0 - не присоединять, 1 - присоединять жестко (INNER JOIN), 2 - присоединять мягко (LEFT JOIN).
    # @param PWS: задает необходимость присоединения таблицы-представления(view) vrbPersonWithSpeciality.  True - присоединять (LEFT JOIN), False - не присоединять.
    # @param ET: задаест способ присоединения таблицы EventType. 0 - не присоединять, 1 - присоединять жестко (INNER JOIN), 2 - присоединять мягко (LEFT JOIN).
    # @param medicalAidTypeCond: добавлять к общему условию (к проверке на deleted=0 и соответствию flatCode указанному значению) условие проверки типа мед. помощи на соответствие стационарному тип.
    # @param Ord: задаёт способ присоединения таблиц для параметра связанного с каналом доставки. 0 — не присоединять, 1 — INNER JOIN, 2 — LEFT JOIN
    def getCondAndQueryTable(self, flatCodeCond, AT = False, APT = 0, AP = 0, APOS = 0, OS = 0, PWS = False, ET = 0, medicalAidTypeCond = True, Ord=0):
        db = QtGui.qApp.db
        cond = [self.tables.Action['deleted'].eq(0),
                self.tables.Action['actionType_id'].inlist(getActionTypeIdListByFlatCode(flatCodeCond))
            ]
        if medicalAidTypeCond:
            cond.append(u'''(EventType.medicalAidType_id IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'1\', \'2\', \'3\', \'7\', \'10\')))''')
        queryTable = self.tables.Action.innerJoin(self.tables.Event, db.joinAnd([self.tables.Action['event_id'].eq(self.tables.Event['id']), self.tables.Event['deleted'].eq(0)]))
        if AT:
            queryTable = queryTable.innerJoin(self.tables.ActionType, self.tables.ActionType['id'].eq(self.tables.Action['actionType_id']))

        queryTable = queryTable.innerJoin(self.tables.Client, db.joinAnd([self.tables.Event['client_id'].eq(self.tables.Client['id']), self.tables.Client['deleted'].eq(0)]))
        if PWS:
            queryTable = queryTable.leftJoin(self.tables.PWS, self.tables.PWS['id'].eq(self.tables.Action['person_id']))

        if APT == 2:
            queryTable = queryTable.leftJoin(self.tables.APT, self.tables.APT['actionType_id'].eq(self.tables.ActionType['id']))
        elif APT == 1:
            queryTable = queryTable.innerJoin(self.tables.APT, self.tables.APT['actionType_id'].eq(self.tables.ActionType['id']))

        if AP == 2:
            queryTable = queryTable.leftJoin(self.tables.AP, db.joinAnd([self.tables.AP['type_id'].eq(self.tables.APT['id']), self.tables.AP['action_id'].eq(self.tables.Action['id']), db.joinOr([self.tables.AP['deleted'].eq(0), self.tables.AP['id'].isNull()])]))
        elif AP == 1:
            queryTable = queryTable.innerJoin(self.tables.AP, db.joinAnd([self.tables.AP['deleted'].eq(0), self.tables.AP['type_id'].eq(self.tables.APT['id']), self.tables.AP['action_id'].eq(self.tables.Action['id'])]))
        if APOS == 2:
            queryTable = queryTable.leftJoin(self.tables.APOS, self.tables.APOS['id'].eq(self.tables.AP['id']))
        elif APOS == 1:
            queryTable = queryTable.innerJoin(self.tables.APOS, self.tables.APOS['id'].eq(self.tables.AP['id']))
        if OS == 2:
            queryTable = queryTable.leftJoin(self.tables.OS, self.tables.OS['id'].eq(self.tables.APOS['value']))
        elif OS == 1:
            queryTable = queryTable.innerJoin(self.tables.OS, self.tables.OS['id'].eq(self.tables.APOS['value']))
        if ET == 1:
            queryTable = queryTable.innerJoin(self.tables.EventType, self.tables.Event['eventType_id'].eq(self.tables.EventType['id']))
        elif ET == 2:
            queryTable = queryTable.leftJoin(self.tables.EventType, self.tables.Event['eventType_id'].eq(self.tables.EventType['id']))

        if Ord == 1:
            queryTable = queryTable.innerJoin(self.tables.OrdAPT, db.joinAnd([
                self.tables.ActionType['id'].eq(self.tables.OrdAPT['actionType_id'])
                , self.tables.ActionType['name'].eq(u'поступление')
                , self.tables.OrdAPT['name'].eq(u'кем доставлен')
                , self.tables.OrdAPT['deleted'].eq(0)
            ]))
            queryTable = queryTable.innerJoin(self.tables.OrdAP, db.joinAnd([
                self.tables.OrdAP['deleted'].eq(0)
                , self.tables.Action['id'].eq(self.tables.OrdAP['action_id'])
                , self.tables.OrdAPT['id'].eq(self.tables.OrdAP['type_id'])
            ]))
            queryTable = queryTable.innerJoin(self.tables.OrdAPS, self.tables.OrdAP['id'].eq(self.tables.OrdAPS['id']))
        elif Ord == 2:
            queryTable = queryTable.leftJoin(self.tables.OrdAPT, db.joinAnd([
                self.tables.ActionType['id'].eq(self.tables.OrdAPT['actionType_id'])
                , self.tables.ActionType['name'].eq(u'поступление')
                , self.tables.OrdAPT['name'].eq(u'кем доставлен')
                , self.tables.OrdAPT['deleted'].eq(0)
            ]))
            queryTable = queryTable.leftJoin(self.tables.OrdAP, db.joinAnd([
                self.tables.OrdAP['deleted'].eq(0)
                , self.tables.Action['id'].eq(self.tables.OrdAP['action_id'])
                , self.tables.OrdAPT['id'].eq(self.tables.OrdAP['type_id'])
            ]))
            queryTable = queryTable.leftJoin(self.tables.OrdAPS, self.tables.OrdAP['id'].eq(self.tables.OrdAPS['id']))

        return queryTable, cond

    def getCondByFilters(self, queryTable, cond, params, withoutAPHB=False):
        db = QtGui.qApp.db
        feed = params.get('feed', 0)
        codeAttachType = params.get('clientAttachTypeCode', 0)
        quotingType = params.get('quotingType', (None, None))
        if feed:
            dateFeed = params.get('dateFeed', QtCore.QDate.currentDate())
            if feed == 1:
                cond.append('NOT %s'%(getEventFeedId(db.formatDate(dateFeed))))
            elif feed == 2:
                cond.append('%s'%(getEventFeedId(db.formatDate(dateFeed))))
        if forceInt(codeAttachType) > 0:
            queryTable = queryTable.innerJoin(self.tables.ClientAttach, db.joinAnd([self.tables.Client['id'].eq(self.tables.ClientAttach['client_id']), self.tables.ClientAttach['deleted'].eq(0)]))
            queryTable = queryTable.innerJoin(self.tables.RBAttachType, db.joinAnd([self.tables.ClientAttach['attachType_id'].eq(self.tables.RBAttachType['id']), self.tables.RBAttachType['code'].eq(codeAttachType)]))
        if quotingType:
            if quotingType[0] != None:
                cond.append(getDataClientQuoting(u'Квота', getQuotingTypeIdList(quotingType)))

        permanent = params.get('permanent', None)
        typeId = params.get('typeId', None)
        profileId = params.get('profileId', None)

        if not withoutAPHB:
            if permanent or typeId or profileId:
                cond.append('''%s''' % (getDataAPHB(permanent, typeId, profileId)))

        return queryTable, cond

    def getItemFromRecord(self, record):
        begDate = forceDateTime(record.value('begDate'))
        endDate = forceDateTime(record.value('endDate'))
        bedCodeName = forceString(record.value('bedCodeName')).split("  ")
        directionDate = forceDateTime(record.value('directionDate'))

        statusObservation = forceString(record.value('statusObservation')).split("  ")
        statusObservationCode = forceString(statusObservation[0]) if len(statusObservation)>=1 else ''
        statusObservationName = forceString(statusObservation[1]) if len(statusObservation)>=2 else ''
        statusObservationColor = forceString(statusObservation[2]) if len(statusObservation)>=3 else ''

        comfortable = forceString(record.value('comfortable'))
        comfortableList = []
        if comfortable:
            comfortableList = comfortable.split("  ")
        comfortableDate = forceDateTime(QtCore.QVariant(comfortableList[0])) if len(comfortableList)>=1 else ''
        comfortableStatus = forceInt(QtCore.QVariant(comfortableList[1])) if len(comfortableList)>=2 else 0
        if comfortableStatus:
            comfortablePayStatus = getRealPayed(comfortableStatus)
        else:
            comfortablePayStatus = False
        birthDate = forceDate(record.value('birthDate'))
        ageString = forceString(calcAge(birthDate, forceDate(endDate)))
        ageInYears = forceInt(calcAgeInYears(birthDate, forceDate(QtCore.QDate().currentDate())))
        sex = forceInt(record.value('sex'))
        item = {'statusObservationCode' : statusObservationCode,
                'nameFinance' : forceString(record.value('nameFinance')),
                'codeFinance' : forceString(record.value('codeFinance')),
                'feed' : forceBool(record.value('countEventFeedId')),
                'physicalActivityName' : forceString(record.value('physicalActivityName')),
                'clientId' : forceRef(record.value('client_id')),
                'contractInfo': '%s %s %s' % tuple(map(lambda f: forceStringEx(record.value(f)), ['contract_number', 'contract_date', 'contract_resolution'])),
                'externalId' : forceString(record.value('externalId')),
                'clientName' : forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')),
                'sex' : self.sex[sex],
                'birthDateRaw' : birthDate,
                'birthDate' : forceString(birthDate),
                'age' : ageString,
                'employable': self.employableCheck(sex, ageInYears),
                'plannedEndDate' : forceDate(record.value('plannedEndDate')),
                'MKB' : forceString(record.value('MKB')),
                'quota':  forceString(record.value('quotaCode')),#quotaTypeClassItems[forceInt(record.value('class'))][0] if forceRef(record.value('class')) >= 0 else u'',
                'codeBed' : forceString(bedCodeName[0]) if len(bedCodeName)>=1 else '' + forceString(bedCodeName[2]) if len(bedCodeName)>=3 else '',
                'nameBed' : forceString(bedCodeName[1]) if len(bedCodeName)>=2 else '',
                'profileBed': forceString(record.value('bedProfile')),
                'nameOS' : forceString(record.value('nameOS')),
                'codeOS' : forceString(record.value('codeOS')),
                'idOS' : forceRef(record.value('idOS')),
                'namePerson' : forceString(record.value('namePerson')),
                'eventId' : forceRef(record.value('eventId')),
                'statusObservationName' : statusObservationName,
                'actionId' : forceRef(record.value('actionId')),
                'actionTypeId' : forceRef(record.value('actionType_id')),
                'statusObservationColor' : statusObservationColor,
                'begDate' : begDate,
                'endDate' : endDate,
                'begDateString' : begDate.toString('dd.MM.yyyy hh:mm'),
                'endDateString' : endDate.toString('dd.MM.yyyy hh:mm'),
                'begDateReceived' : forceDateTime(record.value('setDate')).toString('dd.MM.yyyy hh:mm'),
                'waitingDays': directionDate.daysTo(QtCore.QDateTime.currentDateTime()) if not directionDate.date().isNull() else u'',
                'isHasNotPayedActions' : forceBool(record.value('isExistsNotPayedActions')),     #Определение наличия в событии клиента действий, имеющих тип финансирования ПМУ и без состояния "Оплачено" (задача 482, atronah)
                'comfortableDate' : comfortableDate,
                'comfortablePayStatus' : comfortablePayStatus,
                'patronage': u'да' if forceBool(record.value('patronage')) else u'',
                'currentCommonOSName' : forceStringEx(record.value('currentCommonOSName')),
                'isUnconscious': forceInt(record.value('isUnconscious')),
                'isVIP': forceInt(record.value('isVIP')),
                'vipColor': forceInt(record.value('vipColor')),
                'snils': formatSNILS(forceString(record.value('SNILS'))),
                'directionDate': forceDate(record.value('directionDate'))
                }
        return item

    def sort(self, column, order):
        if column not in xrange(len(self.cols())):
            return

        if not self._columnNamesList:
            self._columnNamesList = [x.fields()[0] for x in self.cols()]

        column = self.cols()[column]
        sortFieldName = column.fields()[0]
        if sortFieldName == 'birthDate' or sortFieldName == 'age' and 'birthDate' in self._columnNamesList:
            sortFieldName = 'birthDateRaw'
        if sortFieldName.endswith('DateString'):
            sortFieldName = sortFieldName[:-6]  # to sort by date, not by date string representation
        self.items.sort(key=lambda item : item.get(sortFieldName, None),
                        reverse = (order == QtCore.Qt.DescendingOrder))
        self.reset()

    def employableCheck(self, sex, ageInYears):
        def check():
            if (ageInYears < 18):
                return False
            if (sex == 1) and (ageInYears < 60):
                return True
            elif (sex == 2) and (ageInYears < 55):
                return True
            return False
        if check():
            return u'Да'
        return u'Нет'

    def getRecordListAdditionalService(self, params, actionType):
        statusObservation = params.get('statusObservation', None)

        osPropertyNameList = [u'Отделение пребывания%']

        db = QtGui.qApp.db
        self.tables.Event = db.table('Event')
        tableStatusObservation= db.table('Client_StatusObservation')

        self.items = []
        cols = self.getQueryCols(statusObservation=True, orgStructurePropertyNameList=osPropertyNameList, PWS=False, dateFeedFlag=True)

        movingActionTable = self.tables.Action.alias('MovingAction')
        queryTable = self.tables.Action.innerJoin(self.tables.Event, self.tables.Action['event_id'].eq(self.tables.Event['id']))
        queryTable = queryTable.innerJoin(self.tables.Client, self.tables.Event['client_id'].eq(self.tables.Client['id']))
        queryTable = queryTable.innerJoin(movingActionTable, [movingActionTable['event_id'].eq(self.tables.Event['id']),
                                                              movingActionTable['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
                                                              movingActionTable['deleted'].eq(0),
                                                              db.joinOr([movingActionTable['begDate'].le(self.tables.Action['endDate']),
                                                                         self.tables.Action['endDate'].isNull()]),
                                                              db.joinOr([movingActionTable['endDate'].ge(self.tables.Action['begDate']),
                                                                         movingActionTable['endDate'].isNull()])
                                                              ])
        cond = [self.tables.Action['actionType_id'].inlist(getActionTypeIdListByFlatCode('%s%%' %actionType)),
                self.tables.Action['deleted'].eq(0),
                self.tables.Event['deleted'].eq(0),
                self.tables.Client['deleted'].eq(0)
                ]


        queryTable = self.compileFinanceCols(cols, cond, queryTable, params.get('financeId', None))

        begDateTime = params.get('begDateTime', None)
        endDateTime = params.get('endDateTime', None)
        changingDayTime = params.get('changingDayTime', QtCore.QTime(0, 0))

        if not begDateTime:
            begDateTime = QtCore.QDateTime().currentDateTime()

        cond.append(db.joinOr([self.tables.Action['endDate'].datetimeGe(begDateTime),
                                   self.tables.Action['endDate'].isNull()]))

        if endDateTime:
            cond.append(self.tables.Action['begDate'].isNotNull())
            cond.append(self.tables.Action['begDate'].datetimeLe(endDateTime))
        else:
            cond.append(movingActionTable['status'].ne(2))
            cond.append(movingActionTable['endDate'].isNull())


        personId = params.get('personId', None)
        if personId:
            cond.append(self.tables.Event['execPerson_id'].eq(personId))

        permanent = params.get('permanent', None)
        typeId = params.get('typeId', None)
        profileId = params.get('profileId', None)
        clientLocation = params.get('clientLocation', 0)
        if clientLocation == 2:
            cond.append('''NOT %s'''%(getDataAPHB()))
        elif clientLocation == 1:
            cond.append('''%s'''%(getDataAPHB(permanent, typeId, profileId)))
        else:
            if (permanent and permanent > 0) or (typeId) or (profileId):
                cond.append('''%s'''%(getDataAPHB(permanent, typeId, profileId)))

        queryTable, cond = self.getCondByFilters(queryTable, cond, params)

        if statusObservation:
                queryTable = queryTable.innerJoin(tableStatusObservation, tableStatusObservation['master_id'].eq(self.tables.Client['id']))
                cond.append(tableStatusObservation['deleted'].eq(0))
                cond.append(tableStatusObservation['statusObservationType_id'].eq(statusObservation))

        return db.getRecordList(queryTable, cols, cond, u'Client.lastName, Client.firstName, Client.patrName')
