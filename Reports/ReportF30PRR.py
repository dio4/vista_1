# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter, getMKBList
from library.database   import addDateInRange
from library.TNMS.TNMSComboBox import convertTNMSStringToDict
from library.Utils      import forceDate, forceInt, forceRef,  forceString, calcAgeInYears, formatName, smartDict
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog

# Добро пожаловать в ад.


def selectClientData(params, result):
    stmt = '''SELECT
        getClientLocAddress(Client.id) as locAddr,
        getClientRegAddress(Client.id) as regAddr,
        getClientContacts(Client.id) as contacts,
        Client.lastName, Client.firstName, Client.patrName,
        Client.birthDate,
        Client.sex
    FROM Client WHERE Client.id = %d LIMIT 1
    ''' % QtGui.qApp.currentClientId()
    query = QtGui.qApp.db.query(stmt)
    query.first()
    record = query.record()
    sex = forceInt(record.value('sex'))
    regAddr = forceString(record.value('regAddr'))
    locAddr = forceString(record.value('locAddr'))
    name = formatName(forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('patrName')))
    birthDate = forceString(record.value('birthDate'))
    contacts = forceString(record.value('contacts'))

    if sex == 1:
        result.sex = u'М - 1'
    elif sex == 2:
        result.sex = u'Ж - 2'
    else:
        result.sex = u'М - 1; Ж - 2'

    result.addr = locAddr if locAddr else regAddr if regAddr else u''
    result.name = name
    result.birthDate = birthDate if birthDate else u'|__| |__| |__|'
    result.birthDate_date = forceDate(record.value('birthDate'))
    result.contacts = contacts if contacts else u'телефон: '
    result.age = u''

def selectSocStatusData(params, result):
    """
        Получение полей:
            13 - Житель (село, город);
            14 - Характеристика лечебного эффекта;
            15 - Локализация отдаленных метастазов;
            16 - Клиническая группа на конец года;
            17 - Группа инвалидности;
            18 - Состояние на конец года;
            19 - Аутопсия
    """
    health_groups = {u'1': u'I',
                     u'2': u'II',
                     u'3': u'III',
                     u'4': u'IV',
                     u'8': u'IIa'}


    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    db = QtGui.qApp.db
    tableClientSocStatus = db.table('ClientSocStatus')
    stmt = '''
    SELECT rbSocStatusClass.code as classCode, rbSocStatusType.name as typeName, rbSocStatusType.code as typeCode
    FROM ClientSocStatus
        INNER JOIN rbSocStatusClass ON rbSocStatusClass.id = ClientSocStatus.socStatusClass_id
                    AND ClientSocStatus.deleted = 0 AND rbSocStatusClass.code IN ('13', '14', '15', '16', '17', '18', '19')
        INNER JOIN rbSocStatusType ON rbSocStatusType.id = ClientSocStatus.socStatusType_id
    WHERE %s
    '''
    cond = [tableClientSocStatus['client_id'].eq(QtGui.qApp.currentClientId())]
    addDateInRange(cond, tableClientSocStatus['begDate'], begDate, endDate)

    sc_dict = smartDict()
    query = db.query(stmt % db.joinAnd(cond))
    while query.next():
        record = query.record()
        classCode = forceString(record.value('classCode'))
        typeCode = forceString(record.value('typeCode'))
        typeName = forceString(record.value('typeName'))
        if classCode == u'16':
            sc_dict[classCode] = health_groups[typeCode] + u' - ' + typeCode
        else:
            sc_dict[classCode] = typeName.lower() + u' - ' + typeCode

    result.socStatus = sc_dict


def selectAttachData(params, result):
    """
        Получение полей:
            8  - Дата смерти;
            11 - Дата обнаружения рецидива;
            12 - Дата перевода в IV клиническую группу;
            13 - ЛУ, осуществляющее диспансерное наблюдение;
            14 - Дата снятия с учёта;
            15 - Дата последнего контакта;
    """
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    db = QtGui.qApp.db
    tableClientAttach = db.table('ClientAttach')
    stmt = '''
    SELECT rbAttachType.code, ClientAttach.begDate, Organisation.infisCode
    FROM ClientAttach
        INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
                    AND ClientAttach.deleted = 0 AND rbAttachType.code IN ('8', '11', '12', '13', '14', '15')
        LEFT JOIN Organisation ON Organisation.deleted = 0 AND Organisation.id = ClientAttach.LPU_id
    WHERE %s
    '''
    cond = [tableClientAttach['client_id'].eq(QtGui.qApp.currentClientId())]
    addDateInRange(cond, tableClientAttach['begDate'], begDate, endDate)

    attach_dict = smartDict()
    query = db.query(stmt % db.joinAnd(cond))
    while query.next():
        record = query.record()
        code = forceString(record.value('code'))
        begDate = forceString(record.value('begDate'))
        orgCode = forceString(record.value('infisCode'))
        if code == '13':
            attach_dict[code] = orgCode
        else:
            attach_dict[code] = begDate

    result.attach = attach_dict


def selectDiagnosisData(params, result):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    MKB = params.get('MKB', None)

    db = QtGui.qApp.db
    tableDiagnosis = db.table('Diagnosis')
    tableEvent = db.table('Event')

    # Только заключительные диагнозы
    stmt = '''
    SELECT Diagnosis.setDate, MKB_Tree.DiagName, Diagnostic.TNMS, Event.id as event_id, Event.setDate, Event.setDate as eventDate, Organisation.fullName as org_name, MKB_Morphology.code as morphologyCode, MKB_Morphology.name as morphologyName
    FROM Event
        INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.diagnosisType_id = 1 AND Event.client_id = %d AND Event.deleted = 0 AND Diagnostic.deleted = 0
        INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.MKB = '%s'
        LEFT JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB
        LEFT JOIN Organisation ON Organisation.id = Event.org_id
        LEFT JOIN MKB_Morphology ON MKB_Morphology.code = Diagnosis.morphologyMKB
    WHERE %s
    ORDER BY Diagnosis.setDate ASC
    '''
    cond = []
    addDateInRange(cond, tableDiagnosis['setDate'], begDate, endDate)
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)

    query = db.query(stmt % (QtGui.qApp.currentClientId(), MKB, db.joinAnd(cond)))
    first = True
    result.events = set()
    minEventDate = QtCore.QDate.currentDate()
    result.diagnostic = smartDict()
    while query.next():
        record = query.record()
        if first:
            setDate = forceString(record.value('setDate'))
            DiagName = forceString(record.value('DiagName'))
            tnms = forceString(record.value('TNMS'))
            age = calcAgeInYears(result.birthDate_date, forceDate(record.value('setDate')))
            orgName = forceString(record.value('org_name'))
            morphologyCode = forceString(record.value('morphologyCode'))
            morphologyName = forceString(record.value('morphologyName'))

            result.diagnostic.setDate = setDate if setDate else u'|__| |__| |__|'
            result.diagnostic.diagName = DiagName if DiagName else u''
            result.diagnostic.tnms = tnms if tnms else u''
            result.diagnostic.organisation = orgName if orgName else u''
            result.diagnostic.morphology = ' '.join((morphologyName, morphologyCode))
            result.age = age
            first = False

        result.events.add(forceRef(record.value('event_id')))
        eventDate = forceDate(record.value('eventDate'))
        if minEventDate > eventDate:
            minEventDate = eventDate

    result.diagnostic.regDate = forceString(minEventDate)

def selectActionsData(params, result):
    """
        Здесь все очень плохо. Вытаскиваем кучу ActionProperty по названиям, переименовываем, приписываем код, засовываем в результат
    """

    pmo_types = {u'синхронная': u'синхронная - 1',
                u'метахронная': u'метахронная - 2',
                u'синхронно-метахронная': u'синхронно-метахронная - 3'}
    lesion_sides = {u'слева': u'слева - 1',
                  u'справа': u'справа - 2',
                  u'двустороннее': u'двусторонняя - 3',
                  u'неприменимо': u'неприменимо - 4',
                  u'неуточненное': u'неуточненная - 5'}
    diagnosis_verification_types = {u'ГИСТОЛОГИЧЕСКИ (ТРЕПАН-БИОПСИЯ)': u'гистол./трепан-биопсия - 01',
                                    u'ЦИТОЛОГИЧЕСКИ (МИЕЛОГРАММА)': u'цитол./миелограмма - 02',
                                    u'РЕНТГЕНОЛОГИЧЕСКИ': u'рентгенол. - 03',
                                    u'ЭНДОСКОПИЧЕСКИ': u'эндоскоп. - 04',
                                    u'ИЗОТОПНЫМ МЕТОДОМ': u'изотопным мет. - 05',
                                    u'ЭХОСКОПИЧЕСКИ (УЗИ)': u'Узи - 06',
                                    u'КЛИНИЧЕСКИ': u'только клинически - 07',
                                    u'ДР.МЕТОДАМИ': u'др. методы - 08',
                                    u'КОМПЬЮТЕРНАЯ ТОМОГРАФИЯ': u'компьютерная томография - 09',
                                    u'БИОХИМИЧ. И/ИЛИ ИММУНОЛ. ТЕСТЫ': u'биохимич. и/или иммунол. тесты - 10',
                                    u'КЛИНИЧ. АНАЛИЗ КРОВИ': u'клинический анализ крови - 11',
                                    u'НА ОПЕРАЦИИ': u'на операци - 12'}
    metastasis_localisation = {u'ЛИМФОУЗЛЫ': u'лимфоузлы - 01',
                               u'КОСТИ': u'кости - 02',
                               u'ПЕЧЕНЬ': u'печень - 03',
                               u'ЛЕГКИЕ/ПЛЕВРА': u'легкие плевра - 04',
                               u'ГОЛОВНОЙ МОЗГ': u'головной мозг - 05',
                               u'КОЖА': u'кожа - 06',
                               u'ПОЧКИ': u'почки - 07',
                               u'ЯИЧНИКИ': u'яичники - 08',
                               u'БРЮШИНЫ': u'брюшины - 09',
                               u'КОСТНЫЙ МОЗГ': u'костный мозг - 10',
                               u'ДР.ОРГАНЫ': u'другие органы - 11',
                               u'МНОЖЕСТВЕННЫЕ': u'множественные - 12'
                               }

    detection_circs = {u'ОБРАТИЛСЯ САМ': u'обратился сам - 1',
                       u'АКТИВНО, В СМОТРОВОМ КАБИНЕТЕ': u'активно, в смотровом кабинете - 2',
                       u'АКТИВНО, ПРИ ПРОФ. ОСМОТРЕ': u'активно, при проф. осмотре - 3',
                       u'ПРИ ДР. ОБСТОЯТЕЛЬСТВАХ': u'при других обстоятельствах - 4',
                       u'НЕТ СВЕДЕНИЙ': u'при других обстоятельствах - 4',
                       u'ОСМОТР СПЕЦИАЛИСТА': u'при других обстоятельствах - 4',
                       u'ПРОФИЛАКТИЧЕСКАЯ ФЛЮОРОГРАФИЯ': u'при других обстоятельствах - 4',
                       u'ЦИТОЛОГИЧЕСКИЙ СКРИНИНГ ШЕЙКИ МАТКИ': u'при других обстоятельствах - 4',
                       u'ПРОФИЛАКТИЧЕСКАЯ МАММОГРАФИЯ': u'при других обстоятельствах - 4',
                       u'ИММУНОФЕРМЕНТНЫЙ СКРИННИНГ РАКА ПР. ЖЕЛ.': u'при других обстоятельствах - 4',
                       u'ДОП. ДИСПАНСЕРИЗАЦИЯ': u'при других обстоятельствах - 4',
                       u'ДИСП. НАБЛЮДЕНИЕ БОЛЬНЫХ С ПРЕДРАКОМ': u'при других обстоятельствах - 4'}

    beg_health_groups = {u'II КЛИНИЧЕСКАЯ ГРУППА (БЕЗ ПОДГУППЫ IIА)': u'II - 2',
                        u'III КЛИНИЧЕСКАЯ ГРУППА': u'III - 3',
                        u'IV КЛИНИЧЕСКАЯ ГРУППА': u'IV - 4',
                        u'УЧТЕН ПОСМЕРТНО,Д-З УСТАНОВЛЕН ПРИ ЖИЗНИ': u'Зарегистрирован посмертно с диагнозом установленным при жизни - 5',
                        u'УЧТЕН ПОСМЕРТНО,Д-З УСТАНОВЛЕН ПОСЛЕ СМЕРТИ,БЕЗ ВСКРЫТИЯ': u'Зарегистрирован посмертно с диагнозом, установленным после смерти без вскрытия - 6',
                        u'УЧТЕН ПОСМЕРТНО,Д-З УСТАНОВЛЕН ПОСЛЕ СМЕРТИ, НА ВСКРЫТИИ': u'Зарегистрирован посмертно после вскрытия',
                        u'IIА КЛИНИЧЕСКАЯ ГРУППА': u'IIa - 8',
                        u'I КЛИНИЧЕСКАЯ ГРУППА': u'I - 1'}

    late_diagnostic_reasons = {
        u'СКРЫТОЕ ТЕЧЕНИЕ БОЛЕЗНИ': u'скрытое течение болезни - 6',
        u'НЕСВОЕВРЕМЕННОЕ ОБРАЩЕНИЕ': u'несвоевременное обращение - 7',
        u'ОТКАЗ ОТ ОБСЛЕДОВАНИЯ': u'отказ от обследования - 8',
        u'НЕПОЛНОЕ ОБСЛЕДОВАНИЕ': u'неполное обследование - 1',
        u'НЕСОВЕРШЕНСТВО ДИСПАНСЕРИЗАЦИИ': u'несовершенство диспансеризации - 5',
        u'ОШИБКА КЛИНИЧЕСКАЯ': u'ошибка: клиническая - 2',
        u'ОШИБКА РЕНТГЕНОЛОГИЧЕСКАЯ': u'ошибка: рентгенологическая - 3',
        u'ОШИБКА МОРФОЛОГИЧЕСКАЯ': u'ошибка: морфологическая',
        u'ОШИБКА ДРУГИХ СПЕЦИАЛИСТОВ': u'др. причины - 9',
        u'ДРУГИЕ ПРИЧИНЫ': u'др. причины - 9'
    }

    oper_characters = {
        u'РАДИКАЛЬНАЯ ОПЕРАЦИЯ': u'радикальная - 3',
        u'ПЛАСТИЧЕСКИЕ И РЕКОНСТРУКТИВНЫЕ': u'прочие - 12',
        u'ПАЛЛИАТИВНАЯ ОПЕРАЦИЯ С УДАЛЕНИЕМ ОПУХОЛИ': u'паллиативная с удалением опухоли - 5',
        u'СИМПТОМАТИЧЕСКАЯ ОПЕРАЦИЯ': u'симптоматическая - 7',
        u'УДАЛЕНИЕ РЕЦИДИВОВ, МЕТАСТАЗОВ': u'удаление метастазов - 8',
        u'ХИРУРГИЧЕСКОЕ ЛЕЧЕНИЕ ОСЛОЖНЕНИЙ ОНКОЗАБОЛЕВАНИЯ': u'прочие - 12',
        u'ХИРУРГИЧЕСКОЕ ЛЕЧЕНИЕ ПОСЛЕОПЕР. ОСЛОЖНЕНИЙ': u'прочие - 12',
        u'ДИАГНОСТИЧЕСКАЯ ОПЕРАЦИЯ': u'диагностическая - 11',
        u'ПРОЧИЕ ОПЕРАЦИИ': u'прочие - 12',
        u'ХИРУРГИЧЕСКАЯ ГОРМОНОТЕРАПИЯ': u'хирургическая гормонотерапия - 13',
        u'ПАЛЛИАТИВНАЯ ОПЕР. С ЧАСТИЧНЫМ УДАЛ. ОПУХОЛИ': u'палл. с частичным удалением опухоли - 6'
    }

    therapy_kind = {
        u'Самостоятельная': u'другая - 3',
        u'Адъювантная': u'адъювантная - 2',
        u'Неадъювантная': u''
    }

    irradiation_methods = {
        u'ДИСТАНЦИОННАЯ': u'дистанционная - 1',
        u'ВНУТРИПОЛОСТНАЯ': u'внутриполостная - 2',
        u'СОЧЕТАННАЯ': u'сочетанная - 3',
        u'ВНУТРИТКАНЕВАЯ': u'внутритканевая - 4',
        u'ДР. ВИДЫ': u'другие виды - 5',
        u'ПРОВЕДЕНО СИМПТОМАТИЧ. ЛЕЧЕНИЕ': u'другие виды - 5'
    }

    irradiation_therapy_types = {
        u'РЕНТГЕНОВСКАЯ': u'рентгеновская - 1',
        u'ГАММАТЕРАПИЯ': u'гамматерапия - 2',
        u'ЭЛЕКТРОНЫ': u'электроны - 3',
        u'ПРОТОНЫ': u'протоны - 4',
        u'ПРОВЕДЕНО СИМПТОМАТИЧ. ЛЕЧЕНИЕ': u'другие виды тормозного излучения - 5',
        u'ДР.ВИДЫ ТОРМОЗНОГО ИЗЛУЧЕНИЯ': u'другие виды тормозного излучения - 5'
    }

    therapy_types = {
        u'ЛЕЧЕБНАЯ': u'лечебная - 1',
        u'АДЪЮВАНТНАЯ': u'адъювантная',
        u'ДРУГАЯ': u'другая - 3'
    }

    treatment_types = {
        u'ХИРУРГИЧЕСКОЕ (ХИР.)': u'хирург (Х) - 01',
        u'ХИМИОТЕРАПЕВТИЧЕСКОЕ (Х/Т)': u'химиотерапия (х/т) - 02',
        u'ГОРМОНОТЕРАПИЯ (ГОРМ.)': u'гормоноиммунотерапия (г/т) - 03',
        u'ЛУЧЕВАЯ ТЕРАПИЯ (ЛУЧ.)': u'лучевая терапия (л/т) - 04',
        u'Х/Т + ХИР.': u'Х+х/т - 05',
        u'Х/Т + ГОРМ.': u'х/т+г/т - 06',
        u'Х/Т + ЛУЧ.': u'х/т+л/т - 07',
        u'Х/Т + ГОРМ. + ХИР.': u'Х+х/т+г/т - 08',
        u'Х/Т + ГОРМ. + ХИР. + ЛУЧ.': u'Х+л/т+х/т+г/т - 09',
        u'ГОРМ. + ХИР.': u'Х+г/т - 10',
        u'ГОРМ. + ХИР. + ЛУЧ.': u'Х+л/т+г/т - 11',
        u'ЛУЧ. + ХИР.': u'Х+л/т - 12',
        u'ЛУЧ. + ГОРМ.': u'л/т+г/т - 13',
        u'ЛУЧ. + ХИМ. + ГОРМ.': u'л/т+х/т+г/т - 14',
        u'ХИР. + ЛУЧ. + ХИМ. ТЕРАП.': u'Х+л/т+х/т'
    }

    treatment_results = {
        u'ОТКАЗАЛСЯ': u'отказался - 1',
        u'ИМЕЛ ПРОТИВОПОКАЗАНИЯ': u'имел противопоказания - 2',
        u'НЕ ПОДЛЕЖАЛ РАДИКАЛЬНОМУ ЛЕЧЕНИЮ': u'не подлежал радик. лечению по распространенности процесса - 3',
        u'ЛЕЧЕНИЕ ПРЕДУСМОТРЕНО В ПОСЛЕДУЮЩЕМ': u'лечение предусмотрено в последующем - 4',
        u'СПЕЦИАЛЬНОЕ ЛЕЧЕНИЕ ПРОВЕДЕНО АМБУЛАТОРНО': u'радик. лечение проведено амбулаторно - 5',
        u'СПЕЦИАЛЬНОЕ ЛЕЧЕНИЕ ПРОВЕДЕНО СТАЦИОНАРНО': u'радик. лечение проведено стационарно - 6'
    }

    db = QtGui.qApp.db

    oper_group_id = forceRef(db.translate('ActionType', 'code', 'oper', 'id'))



    stmt = u'''
    SELECT ActionType.code as AT_code, ActionType.name AS AT_name, ActionType.group_id as AT_group_id, ActionPropertyType.name AS APT_name, ActionProperty_String.value, ActionProperty_Date.value as date_value, Action.begDate, Action.endDate, ActionProperty.id as AP_id
    FROM Action
        INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0 AND Action.deleted = 0 AND Action.event_id IN (%s)
        LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0
        LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
        LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
        LEFT JOIN ActionProperty_Date ON ActionProperty_Date.id = ActionProperty.id
    '''

    result.actions = smartDict()
    actions = result.actions
    treatment = result.actions.setdefault('treatment', smartDict())
    chemotherapy = actions.setdefault('chemotherapy', smartDict())
    beam_therapy = actions.setdefault('beam_therapy', smartDict())
    hormonal_therapy = actions.setdefault('hormonal_therapy', smartDict())


    query = db.query(stmt % u'0' if not result.events else u', '.join(str(event) for event in result.events))
    while query.next():
        record = query.record()
        AT_code = forceString(record.value('AT_code'))
        APT_name = forceString(record.value('APT_name')).lower()
        AT_group_id = forceRef(record.value('AT_group_id'))

        AP_id = forceRef(record.value('AP_id'))
        if AP_id and AT_code == u'setdiagn':
            value = forceString(record.value('value'))
            if APT_name == u'вид пмо':
                actions.pmo_type = pmo_types.setdefault(value.lower(), u'синхронная - 1; метахронная - 2; синхронно-метахронная - 3')
            elif APT_name == u'причинно-множественная опухоль':
                if value.lower() == u'нет':
                    actions.pmo = value + u' - 9'
                elif value:
                    actions.pmo = u'да - ' + value
                else:
                    actions.pmo = u'нет - 9; да - 2-я; 3-я; 4-я; 5-я; 6-я; 7-я; 8-я'

            elif APT_name == u'метод подтверждения диагноза':
                actions.diagnosis_verification = diagnosis_verification_types.setdefault(value, u'гистол.- 01;   цитол. - 02;   \
                компьютерная томография - 09; рентгенол.- 03; Узи - 06;   эндоском.- 04; изотопным мет.- 05; на операции - 12; \
                биохимич. и/или иммунол.тесты - 10; другие методы - 08; только клинически - 07;\nдля лейкозов: трепан-биопсия - 01; \
                миелограмма - 02; клинический анализ крови - 11')

            elif APT_name == u'сторона поражения':
                actions.lesion_side = lesion_sides.setdefault(value.lower(), u'слева - 1; справа - 2; двусторонняя - 3; неприменимо - 4; неуточненная - 5')

            elif APT_name == u'степень дифференцировки':
                actions.morphology_type = forceString(value.lower())

            elif APT_name == u'локализация отдаленных метастазов':
                actions.metastasis_localisation = \
                    metastasis_localisation.setdefault(value, u'лимфоузлы - 01; кости - 02; печень - 03; легкие плевра - 04; головной мозг - 05; кожа - 06;\
                    почки - 07; яичники - 08; брюшина - 09; костный мозг - 10; другие органы - 11; множественные - 12')

            elif APT_name == u'обстоятельства выявления опухоли':
                actions.detection_circs = detection_circs.setdefault(value, u'обратился сам - 1; активно, в смотровом кабинете - 2; активно, при проф. осмотре - 3; при других обстоятельствах - 4')

            elif APT_name == u'взят на учет с клинической группой':
                actions.beg_health_group = beg_health_groups.setdefault(value, u'I - 1; II - 2; IIa - 8; III - 3; IV - 4; \nЗарегистрирован посмертно: с диагнозом, установленным при жизни - 5; после смерти без вскрытия - 6; после вскрытия - 7')

            elif APT_name == u'причина поздней диагностики':
                actions.late_diagnostic_reason = late_diagnostic_reasons.setdefault(value, u'скрытое течение болезни - 6; несвоевременное обращение - 7; отказ от обследования - 8; неполное обследование - 1; несовершенство диспансеризации - 5;\nошибка: клиническая - 2; рентгенологическая - 3; морфологическая - 4; др. причины - 9')

        if AT_code == u'oper':
            actions.oper_date = forceString(forceDate(record.value('endDate')))
            if APT_name == u'характер операции':
                actions.oper_character = oper_characters.setdefault(forceString(record.value('value')), u'радикальная - 3; паллиативная с удалением опухоли - 5; палл. с частичным удалением опухоли - 6; удаление метастазов - 8; симптоматическая - 7; диагностическая - 11; хирургическая гормонотерапия - 13; прочие - 12')

        elif AP_id and AT_code == u'gormonotherapy':
            #if APT_name == u'вид':
            if APT_name == u'дата начала':
                value = forceString(record.value('date_value'))
                hormonal_therapy.date = value
        elif AP_id and AT_code == u'beamtherapy':
            if APT_name == u'дата начала':
                value = forceString(record.value('date_value'))
                beam_therapy.date = value
            elif APT_name == u'способ облучения':
                value = forceString(record.value('value'))
                beam_therapy.irradiation_method = irradiation_methods.setdefault(value, u'дистанционная - 1; внутриполостная - 2; сочетанная - 3; внутритканевая - 4; другие виды - 5')
            elif APT_name == u'вид':
                value = forceString(record.value('value'))
                beam_therapy.type = irradiation_therapy_types.setdefault(value, u'рентгеновская - 1; гамматерапия - 2; электроны - 3; протоны - 4; другие виды тормозного излучения - 5')
        elif AP_id and AT_code == u'himtherapy':
            if APT_name == u'дата начала':
                value = forceString(record.value('date_value'))
                chemotherapy.date = value
            elif APT_name == u'Тип':
                value = forceString(record.value('value'))
                chemotherapy.type = therapy_types.setdefault(value, u'лечебная - 1; адъювантная - 2; другая - 3')
        elif AP_id and AT_code == u'treatment':
            treatment_result = treatment.setdefault('result', u'')
            value = forceString(record.value('value'))

            if APT_name == u'вид проведенного специального лечения':
                treatment.type = treatment_types.setdefault(value, u'хирург (Х) - 01; химиотерапия (х/т) - 02; гормоноиммунотерапия (г/т) - 03; лучевая терапия (л/т) - 04; Х+х/т - 05; х/т+г/т - 06; х/т+л/т - 07; Х+х/т+г/т - 08; Х+л/т+х/т+г/т - 09; Х+г/т - 10; Х+л/т+г/т - 11; Х+л/т - 12; л/т+г/т - 13; л/т+х/т+г/т - 14; Х+л/т+х/т - 15')
            elif not treatment_result and APT_name == u'специальное лечение' or APT_name == u'специальное лечение проведено':
                treatment.result = treatment_results.setdefault(value, u'')
        if oper_group_id and AT_group_id == oper_group_id:
            actions.oper_name = forceString(record.value('AT_name'))




def selectData(params):
    """
        1) Пока что считается, что в базу будут заводиться только несколько Ф.27 и одна-две Ф.30. Больше - ничего
           Поэтому в запросе мы не привязываемся к типу события, берем все что есть.
    """
    result = smartDict()
    selectClientData(params, result)
    selectSocStatusData(params, result)
    selectAttachData(params, result)
    selectDiagnosisData(params, result)
    selectActionsData(params, result)
    return result




class CReportF30PRR(CReport):
    
    errNoNosology = u'За выбранный период у данного пациента не обнаружено ни одного установленного диагноза. Пожалуйста, выберите другой период.'
    
    primaryMap = {1: u'первичные',
                  2: u'повторные',
                  3: u'активные посещения',
                  4: u'перевозки',
                  5: u'амбулаторные'}
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'РЕГИСТРАЦИОННАЯ КАРТА БОЛЬНОГО ЗЛОКАЧЕСТВЕННЫМ НОВООБРАЗОВАНИЕМ*')
        self.parent = parent

    #TODO: atronah: поскольку большая часть кода функции ниже взята из CReportBase.reportLoop
    # то считаю разумным унаследоваться от нее, а необходимость двухэтапной обработки выбора пользователя
    # перенести с логики "двух диалогов" (из-за которых и создавался клон функции, как я понял)
    # на логику "двух-страничного диалога" (с использованием QStackedWidget)
    def reportLoop(self):
        params = self.getDefaultParams()
        while True:
            setupDialog = self.getSetupDialog(self.parent)
            setupDialog.setParams(params)
            if not setupDialog.exec_() :
                break
            params = setupDialog.params()
            setupSubsidiaryDialog = self.getSubsidiarySetupDialog(self.parent)
            success = setupSubsidiaryDialog.setParams(params)
            if not success:
                QtGui.QMessageBox.critical(self.parent,
                                     u'Внимание!',
                                     CReportF30PRR.errNoNosology,
                                     QtGui.QMessageBox.Ok,
                                     QtGui.QMessageBox.Ok)
                continue
            if not setupSubsidiaryDialog.exec_() :
                break
            paramsSubsidiary = setupSubsidiaryDialog.params()
            self.saveDefaultParams(paramsSubsidiary)
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                reportResult = self.build(paramsSubsidiary)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            viewDialog = CReportViewDialog(self.parent)
            if self.viewerGeometry:
                viewDialog.restoreGeometry(self.viewerGeometry)
            viewDialog.setWindowTitle(self.title())
            viewDialog.setRepeatButtonVisible()
            viewDialog.setText(reportResult)
            done = not viewDialog.exec_()
            self.viewerGeometry = viewDialog.saveGeometry()
            if done:
                break

    def getSetupDialog(self, parent):
        result = CReportF30PRRSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def getSubsidiarySetupDialog(self, parent):
        result = CReportF30PRRSubsidiarySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def getDescription(self, params):
        rows = CReport.getDescription(self, params)
        primary = params.get('primaryStatus', 0)
        if primary:
            rows.append(u'Признак первичности: ' + self.primaryMap[primary])
        return rows


    def build(self, params):
        result = selectData(params)

        # now text
        doc = QtGui.QTextDocument()
        boldFormat = QtGui.QTextCharFormat()
        boldFormat.setFontWeight(QtGui.QFont.Bold)
        boldFormat.setFontPointSize(8)

        italicFormat = QtGui.QTextCharFormat()
        italicFormat.setFontItalic(True)
        italicFormat.setFontPointSize(8)

        boldItalicFormat = QtGui.QTextCharFormat()
        boldItalicFormat.setFontItalic(True)
        boldItalicFormat.setFontWeight(QtGui.QFont.DemiBold)
        boldItalicFormat.setFontPointSize(8)

        plainFormat = QtGui.QTextCharFormat()
        plainFormat.setFontWeight(QtGui.QFont.Normal)
        plainFormat.setFontPointSize(8)

        plainBlockFormat = QtGui.QTextBlockFormat()

        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)

        cursor.insertBlock()
        cursor.setCharFormat(boldItalicFormat)
        cursor.insertText(u'Популяционный раковый регистр Санкт-Петербурга')

        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())


        #cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'Ф. №030 - 6/ГРР')

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'   %d № амбулаторной карты\n' % QtGui.qApp.currentClientId())

        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'1. Номер регистрационной карты \n')
        cursor.insertText(u'2. %s (лечебное учреждение, осуществляющее диспансерное наблюдение)\n' % result.attach.setdefault('13', u''))

        cursor.insertBlock()
        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'3. Дата поступления сведений о случае заболевания в регистр\n')

        cursor.insertBlock()
        cursor.insertText(u'Ф.И.О. ', boldFormat)
        cursor.insertText(result.name + u'\n', plainFormat)
        cursor.insertText(u'4. Адрес: ', boldFormat)
        cursor.insertText(result.addr + u'\n', plainFormat)


        cursor.insertBlock()
        cols = [(u'50%', u'', CReportBase.AlignLeft),(u'50%', u'', CReportBase.AlignLeft)]
        table = createTable(cursor, cols, headerRowCount = 0, border = 0)
        i = table.addRow()
        table.setText(i, 0, result.contacts)
        table.setText(i, 1, u'5. Район', boldFormat)

        i = table.addRow()
        c = table.cursorAt(i, 0)
        c.insertText(u'6. Житель:  ', boldFormat)
        c.insertText(result.socStatus.setdefault('13', u'города - 1; села - 2 **'), plainFormat)
        c = table.cursorAt(i, 1)
        c.insertText(u'Пол: ', boldFormat)
        c.insertText(result.sex, plainFormat)

        i = table.addRow()
        table.setText(i, 0, u'Национальность', boldFormat)

        i = table.addRow()
        c = table.cursorAt(i, 0)
        c.insertText(u'Дата рождения: ', boldFormat)
        c.insertText(result.birthDate, plainFormat)
        c = table.cursorAt(i, 1)
        c.insertText(u'Возраст ', boldFormat)
        c.insertText(u'в момент\nустановления диагноза: %s' % result.age, plainFormat)
        #cursor.movePosition(QtGui.QTextCursor.End)

        #cursor.insertBlock()
        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'9. Социально-профессиональная группа (профессия, преобладающая в течение жизни)')

        i = table.addRow()
        cols = [(u'90%', u'', CReportBase.AlignCenter)]
        tblSetDate = table.setTable(i, 0, cols, 0)
        c = tblSetDate.cursorAt(0, 0)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'  Дата установления диагноза\t\n', boldFormat)
        c.insertText(result.diagnostic.setdefault('setDate', u'|__| |__| |__|'), plainFormat)
        tblRegisterDate = table.setTable(i, 1, cols, 0)
        c = tblRegisterDate.cursorAt(0, 0)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'  \tДата регистрации\t\t\n', boldFormat)
        c.insertText(result.diagnostic.setdefault('regDate', u'|__| |__| |__|'), plainFormat)

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        c = table.cursorAt(i, 0)
        c.insertText(u'12. Место установления диагноза: ', boldFormat)
        c.insertText(result.diagnostic.get('organisation', ''), plainFormat)


        i = table.addRow()
        c = table.cursorAt(i, 0)
        c.insertText(u'13. Обстоятельства выявления опухоли:\n', boldFormat)
        c.insertText(result.actions.setdefault(u'detection_circs', u'обратился сам - 1; активно, в смотровом кабинете - 2; активно, при проф. осмотре - 3; при других обстоятельствах - 4') + u'\n\n', plainFormat)
        c.insertText(u'14. Первично-множественная опухоль:\n', boldFormat)
        c.insertText(result.actions.setdefault(u'pmo', u'нет - 9; да -  2-я; 3-я; 4-я; 5-я; 6-я; 7-я; 8-я') + u'\n\n', plainFormat)
        c.insertText(u'Если ПМО, ', boldFormat)
        c.insertText(result.actions.setdefault(u'pmo_type', u'то синхронная - 1; метахронная - 2; синхронно-метахронная - 3') + u'\n\n', plainFormat)

        cols = [(u'20%', [u'Первично-множественные опухоли', u'№'], CReportBase.AlignLeft),
                (u'30%', [u'', u'МКБ-10'], CReportBase.AlignLeft),
                (u'30%', [u'', u'Год'], CReportBase.AlignLeft),
                (u'30%', [u'', u'Вид леч.'], CReportBase.AlignLeft)]
        tableTumors = table.setTable(i, 1, cols)
        tableTumors.mergeCells(0, 0, 1, 4)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.insertText(u'16. Диагноз: ', boldFormat)
        cursor.insertText(result.diagnostic.get('diagName', '') + u'\nСторона поражения: ', plainFormat)
        cursor.insertText(result.actions.setdefault(u'lesion_side', u'слева - 1; справа - 2; двусторонняя - 3; неприменимо - 4; неуточненная - 5') + u'\n', plainFormat)

        cols = [(u'30%', u'', CReportBase.AlignCenter),
                (u'70%', u'', CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        c = table.cursorAt(0, 0)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'17. Стадия по системе\n', boldFormat)
        tnms = convertTNMSStringToDict(result.diagnostic.get('tnms', ''))
        T = tnms.setdefault('cT', u'')
        if T == 'x':
            T = u''
        N = tnms.setdefault('cN', u'')
        if N == 'x':
            N = u''
        M = tnms.setdefault('cM', u'')
        if M == 'x':
            M = u''
        c.insertText(u'T%s N%s M%s' % (T, N, M), plainFormat)

        c = table.cursorAt(0, 1)
        c.insertText(u'18. Группировка по стадиям ', boldFormat)
        c.insertText(u'(нужное обвести кружком):\nIA, UB, IC, I;    IIA, IIB, IIC, II;    IIIA, IIIB, IIIC, III;    IVA, IVB, IVC, IV; in situ; неприменимо; неизвестно |__|__|', plainFormat)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.insertText(u'\nЛокализация отдаленных метастазов ', boldFormat)
        cursor.insertText(u'при IV стадии: %s\n' % (result.actions.setdefault('metastasis_localisation', u'лимфоузлы - 01; кости - 02; печень - 03; легкие плевра - 04; головной мозг - 05; кожа - 06; почки - 07; яичники - 08; брюшина - 09; костный мозг - 10; другие органы - 11; множественные - 12')), plainFormat)
        #c.insertText(u'при IV стадии: лимфоузлы - 01; кости - 02; печень - 03; легкие плевра - 03')

        cursor.insertText(u'\n19. Диагноз подтвержден: ', boldFormat)
        cursor.insertText(result.actions.setdefault(u'diagnosis_verification', u'гистол.- 01;   цитол. - 02;   \
                компьютерная томография - 09; рентгенол.- 03; Узи - 06;   эндоском.- 04; изотопным мет.- 05; на операции - 12; \
                биохимич. и/или иммунол.тесты - 10; другие методы - 08; только клинически - 07;\nдля лейкозов: трепан-биопсия - 01; \
                миелограмма - 02; клинический анализ крови - 11') + u'\n', plainFormat)
        cursor.insertText(u'\n20. Морфологический тип опухоли: ', boldFormat)
        cursor.insertText(result.diagnostic.get('morphology', ''), plainFormat)
        cursor.insertText(u'\nСтепень дифференцировки: ', plainFormat)
        cursor.insertText(result.actions.setdefault(u'morphology_type', u'') + u'\n', plainFormat)
        cursor.insertText(u'\n21. Состоял на учете: \n', boldFormat)

        cursor.insertText(u'\n22. Взят на учет с клинической группой: ', boldFormat)
        cursor.insertText(result.actions.setdefault(u'beg_health_group', u'I - 1; II - 2; IIa - 8; III - 3; IV - 4; \nЗарегистрирован посмертно: с диагнозом, установленным при жизни - 5; после смерти без вскрытия - 6; после вскрытия - 7') + u'\n', plainFormat)
        cursor.insertText(u'\n23. Причина поздней диагностики: ', boldFormat)
        cursor.insertText(u'указывается при выявлении злок. опухоли в IV ст., а при визуальной локализации - с III ст.' + result.actions.setdefault(u'late_diagnostic_reason', u'скрытое течение болезни - 6; несвоевременное обращение - 7; отказ от обследования - 8; неполное обследование - 1; несовершенство диспансеризации - 5;\nошибка: клиническая - 2; рентгенологическая - 3; морфологическая - 4; др. причины - 9') + u'\n', plainFormat)
        cursor.insertText(u'\n24. Лечение первичной опухоли:\n', boldFormat)
        cursor.insertText(u'\n25. Радикальное лечение: ', boldFormat)
        cursor.insertText(result.actions.treatment.setdefault(u'result', u'отказался - 1; имел противопоказания - 2; не подлежал радик. лечению по распространенности процесса - 3; лечение предусмотрено в последующем - 4; радик. лечение проведено амбулаторно - 5; радик. лечение проведено стационарно - 6.') + u'\n', plainFormat)

        cursor.insertBlock()
        table = createTable(cursor, [(u'70%', u'', CReportBase.AlignLeft), (u'30%', u'', CReportBase.AlignLeft)])
        c = table.cursorAt(0, 0)
        c.insertText(u'26. Вид проведенного специального лечения в течение года:\n', boldFormat)
        c.insertText(result.actions.treatment.setdefault(u'type', u'хирург (Х) - 01; химиотерапия (х/т) - 02; гормоноиммунотерапия (г/т) - 03; лучевая терапия (л/т) - 04; Х+х/т - 05; х/т+г/т - 06; х/т+л/т - 07; Х+х/т+г/т - 08; Х+л/т+х/т+г/т - 09; Х+г/т - 10; Х+л/т+г/т - 11; Х+л/т - 12; л/т+г/т - 13; л/т+х/т+г/т - 14; Х+л/т+х/т - 15'), plainFormat)
        c = table.cursorAt(0, 1)
        c.insertText(u'20__г._________\n20__г._________\n20__г._________', plainFormat)


        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\n')
        cols = [(u'60%', [u'27. Место проведения спец. лечения и вид лечения в указанном леч. учреждении', u'Наименование леч. учреждения'], CReportBase.AlignLeft),
                (u'10%', [u'', u'Год'], CReportBase.AlignCenter),
                (u'40%', [u'', u'Вид лечения в данном стационаре'], CReportBase.AlignCenter)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 3)
        table.addRow()
        table.addRow()
        table.addRow()


        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\n28. Тип стационара, где лечился больной:\n', boldFormat)

        cursor.insertBlock()
        table = createTable(cursor, [(u'70%', u'', CReportBase.AlignLeft), (u'30%', u'', CReportBase.AlignCenter)])
        c = table.cursorAt(0, 0)
        c.insertText(u'29. Характер операции: ', boldFormat)
        c.insertText(result.actions.setdefault(u'oper_character', u'радикальная - 3; паллиативная с удалением опухоли - 5; палл. с частичным удалением опухоли - 6; удаление метастазов - 8; симптоматическая - 7; диагностическая - 11; хирургическая гормонотерапия - 13; прочие - 12') + u'\n', plainFormat)
        c = table.cursorAt(0, 1)
        c.insertText(u'30. Дата операции:\n', boldFormat)
        c.insertText(result.actions.setdefault(u'oper_date', u'|__| |__| |__|'), plainFormat)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\n31. Название операции: ', boldFormat)
        cursor.insertText(result.actions.setdefault('oper_name', u'\n\n') + u'\n', plainFormat)

        cursor.insertBlock(plainBlockFormat)
        cursor.insertText(u'\n')
        table = createTable(cursor, [(u'40%', u'', CReportBase.AlignLeft), (u'60%', u'', CReportBase.AlignLeft)])
        c = table.cursorAt(0, 0)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'32. Дата начала лучевой терапии\n', boldFormat)
        c.insertText(result.actions.beam_therapy.setdefault('date', u'|__| |__| |__|'), plainFormat)
        c = table.cursorAt(0, 1)
        c.insertText(u'33. Способ облучения: ', boldFormat)
        c.insertText(result.actions.beam_therapy.setdefault('irradiation_method', u'дистанционная - 1; внутриполостная - 2; сочетанная - 3; внутритканевая - 4; другие виды - 5') + u'\n', plainFormat)
        c.insertText(u'Вид облучения: ', boldFormat)
        c.insertText(result.actions.beam_therapy.setdefault('type', u'рентгеновская - 1; гамматерапия - 2; электроны - 3; протоны - 4; другие виды тормозного излучения - 5'), plainFormat)

        i = table.addRow()
        c = table.cursorAt(i, 0)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'34. Дата начала химиотерапии\n', boldFormat)
        c.insertText(result.actions.chemotherapy.setdefault('date', u'|__| |__| |__|'), plainFormat)

        c = table.cursorAt(i, 1)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'35. Дата начала гормонотерапии\n', boldFormat)
        c.insertText(result.actions.hormonal_therapy.setdefault('date', u'|__| |__| |__|'), plainFormat)


        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\n36. Характеристика лечебного эффекта ', boldFormat)
        cursor.insertText(u'(для больных, завершивших радикальное лечение): ' + result.socStatus.setdefault(u'14', u'опухоль излечена - 1; спец. лечение оказалось неэффективным - 2; рецидив - 3; рег. метастазы - 4; отдал. метастазы - 5; рецидив и метастазы - 6; ремиссия системного заболевания - 7; лейкемизация лимфом - 8; прогрессирование системного заболевания - 9') + u'\n', plainFormat)

        cursor.insertBlock()
        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 50), QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 50)])
        table = createTable(cursor, [(u'50%', [u''], CReportBase.AlignCenter), (u'60%', [u''], CReportBase.AlignCenter)])
        table.table.setFormat(tableFormat)
        c = table.cursorAt(0, 0)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'37. Дата обнаружения рецидива или метастаза:\n', boldFormat)
        c.insertText(result.attach.setdefault('11', u'|__| |__| |__|'), plainFormat)
        c = table.cursorAt(0, 1)
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'38. Локализация отдаленных метастазов:\n', boldFormat)
        c.insertText(result.socStatus.setdefault('15', u'_____________|__|__|'))

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\n39. Клиническая группа на конец года: ', boldFormat)
        cursor.insertText(result.socStatus.setdefault('16', u'I - 1; II - 2; IIa - 8; III - 3; IV - 4') + u'\n', plainFormat)
        cursor.insertText(u'Дата перевода в IV клиническую группу: ', plainFormat)
        cursor.insertText(result.attach.setdefault('12', u'|__| |__| |__|') + u'\n', plainFormat)

        cursor.insertText(u'\n40. Группа инвалидности: ', boldFormat)
        cursor.insertText(result.socStatus.setdefault('17', u'I - 1; II - 2; III - 3; реабилитация - 4; не имел - 5; инвалид детства - 6') + u'\n', plainFormat)

        cursor.insertText(u'\n41. Состояние на конец года: ', boldFormat)
        cursor.insertText(result.socStatus.setdefault('18', u'состоит на учете - 1; умер: в результате осложнений, связанных с лечением - 2; от основного злокачественного новообразования - 3; от др. заболеваний - 4; снят с учета: по базалиоме - 5; выехал - 6; диагноз не подтвердился - 7') + u'\n', plainFormat)

        cursor.insertBlock(CReportBase.AlignCenter)
        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setBorder(0)
        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 40), QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 20), QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 40)])
        table = cursor.insertTable(1, 3, tableFormat)

        c = table.cellAt(0, 0).lastCursorPosition()

        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 100)])
        tableFormat.setBorder(1)
        tableFormat.setCellPadding(0)
        tableFormat.setCellSpacing(0)


        tblDeathDate = c.insertTable(1, 1, tableFormat)
        c = tblDeathDate.cellAt(0, 0).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'42. Дата смерти\n', boldFormat)
        c.insertText(result.attach.setdefault('8', u'|__| |__| |__|'), plainFormat)

        c = table.cellAt(0, 1).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'или', plainFormat)

        c = table.cellAt(0, 2).lastCursorPosition()
        tblLeaveDate = c.insertTable(1, 1, tableFormat)
        c = tblLeaveDate.cellAt(0, 0).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignCenter)
        c.insertText(u'Дата снятия с учета\n', boldFormat)
        c.insertText(result.attach.setdefault('14', u'|__| |__| |__|'), plainFormat)

        cursor.movePosition(QtGui.QTextCursor.End)
        # Вставить таблицу с датой смерти/снятия с учета

        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.insertText(u'\n43. В случае смерти: ', boldFormat)
        cursor.insertText(u'аутопсия ' + result.socStatus.setdefault('19', u'производилась - 1; не производилась - 2') + u'\n', plainFormat)

        cursor.insertText(u'\n44. Причина смерти ', boldFormat)
        cursor.insertText(u'(заболевание, послужившее основной причиной смерти): ', plainFormat)
        if result.attach['8'] and result.attach['8'] != u'|__| |__| |__|':
            cursor.insertText(params.get('MKB', u''), plainFormat)
        cursor.insertText(u'\n', plainFormat)

        cursor.insertText(u'\n45. Дата последнего контакта: ', boldFormat)
        cursor.insertText(result.attach.setdefault('15', u'') + u'\n', plainFormat)

        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'Отметки о патронаже (II) или вызове (В) больного')
        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 14.14) for i in range(7)])
        #tableFormat.setBorderStyle(QtGui.QTextFrameFormat.BorderStyle_Solid)
        tableFormat.setBorder(1)
        tableFormat.setCellPadding(0)
        tableFormat.setCellSpacing(0)
        cursor.insertTable(2, 7, tableFormat)

        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertText(u'Отметки о проведении диспансерных осмотров')

        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 12.5) for i in range(8)])
        #tableFormat.setBorderStyle(QtGui.QTextFrameFormat.BorderStyle_Solid)
        tableFormat.setBorder(1)
        tableFormat.setCellPadding(0)
        tableFormat.setCellSpacing(0)
        table = cursor.insertTable(6, 8, tableFormat)
        c = table.cellAt(0, 0).lastCursorPosition()
        c.insertText(u'Назначено явиться')
        c = table.cellAt(1, 0).lastCursorPosition()
        c.insertText(u'Явился')
        c = table.cellAt(2, 0).lastCursorPosition()
        c.insertText(u'Назначено явиться')
        c = table.cellAt(3, 0).lastCursorPosition()
        c.insertText(u'Явился')
        c = table.cellAt(4, 0).lastCursorPosition()
        c.insertText(u'Назначено явиться')
        c = table.cellAt(5, 0).lastCursorPosition()
        c.insertText(u'Явился')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock(CReportBase.AlignLeft)

        cursor.insertText(u'\n\n\nФ.И.О. врача и его подпись: \n', boldFormat)
        cursor.insertText(u'Дата заполнения карты: "____" ____________', plainFormat)

        return doc


from Ui_ReportF30PRRSetup import Ui_ReportF30PRRSetupDialog


class CReportF30PRRSetupDialog(QtGui.QDialog, Ui_ReportF30PRRSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
            

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()

        return result


    @QtCore.pyqtSlot(bool)
    def on_chkUseInputDate_toggled(self, checked):
        self.lblBegInputDate.setEnabled(checked)
        self.edtBegInputDate.setEnabled(checked)
        self.lblEndInputDate.setEnabled(checked)
        self.edtEndInputDate.setEnabled(checked)


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)

from Ui_ReportF30PRRSubsidiarySetup import Ui_ReportF30PRRSubsidiarySetupDialog

class CReportF30PRRSubsidiarySetupDialog(QtGui.QDialog, Ui_ReportF30PRRSubsidiarySetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.paramsSubsidiary = {}
        self.edtDiagnosis.textChanged.connect(self.checkMKB)
    
    @QtCore.pyqtSlot(QtCore.QString)
    def checkMKB(self, newText):
        btnOk = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        btnOk.setEnabled(self.edtDiagnosis.findText(newText) != -1)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.Subsidiary = params
        self.setTitle(u'Выберите диагноз')
        return self.getFilterMKB()

    def params(self):
        self.Subsidiary['MKB'] = self.edtDiagnosis.text()
        return self.Subsidiary
    
    def getFilterMKB(self):
        self.edtDiagnosis.clear()
        begDate                = self.Subsidiary.get('begDate', None)
        endDate                = self.Subsidiary.get('endDate', None)
        
        mkbList = getMKBList(begDate, endDate)
        if not mkbList:
            return False
        
        self.edtDiagnosis.addItems(mkbList)
        return True