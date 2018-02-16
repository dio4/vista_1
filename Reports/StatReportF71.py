# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.MapCode    import createMapCodeToRowIdx
from library.Utils      import forceBool, forceInt, forceString
from Orgs.Utils         import getOrgStructureDescendants, getOrgStructures
from Reports.Report     import CReport, normalizeMKB
from Reports.ReportAcuteInfections import CReportAcuteInfectionsSetupDialog
from Reports.ReportBase import createTable, CReportBase


Rows = [
    ('-', 'A00-T98', u'Всего'),
    ('1', 'A00-B99', u'Некоторые инфекционные и паразитарные болезни'),
    ('1.1', 'A00-A09', u'Кишечные инфекции'),
    ('1.1.1', 'A01', u'Тиф и паратиф'),
    ('1.1.2', 'A02', u'Другие сальмонелезные инфекции'),
    ('1.1.3', 'A03', u'Шигелез'),
    ('1.1.4', 'A04', u'Другие бактериальные кишечные инфекции'),
    ('1.1.5', 'A05', u'Другие бактериальные пищевые отравления'),
    ('1.1.6', 'A07.1', u'Лямблиоз'),
    ('1.1.7', 'A08', u'Вирусные и другие уточненные кишечные инфекции'),
    ('1.1.8', 'A09', u'Диарея и гастроэнтерит предположительно инфекционного происхождения'),
    ('1.2', 'A28.2', u'Экстраинтестинальный иерсиниоз'),
    ('1.3', 'A30-A39', u'Бактериальные инфекции'),
    ('1.3.1', 'A36', u'Дифтерия'),
    ('1.3.2', 'A37', u'Коклюш'),
    ('1.3.3', 'A38', u'Скарлатина'),
    ('1.3.4', 'A39', u'Менингококковая инфекция'),
    ('1.3.5', 'A40-A41', u'Септицемия стрептококковая и др.'),
    ('1.4', 'A80-A89', u'Вирусные инфекции центральной нервной системы'),
    ('1.4.1', 'A86-A87', u'Вирусный энцефалит и менингит'),
    ('1.5', 'B00-B09', u'Вирусные инфекции, характеризующиеся поражениями кожи и слизистых оболочек'),
    ('1.5.1', 'B01', u'Ветряная оспа'),
    ('1.5.2', 'B05', u'Корь'),
    ('1.5.3', 'B06', u'Краснуха'),
    ('1.6', 'B15-B19', u'Вирусный гепатит'),
    ('1.6.1', 'B15', u'Острый гепатит A'),
    ('1.6.2', 'B16', u'Острый гепатит B'),
    ('1.7', 'B20-B24', u'Болезнь, вызванная вирусом иммунодефицита человека [ВИЧ]'),
    ('1.8', 'B25-B34', u'Другие вирусные болезни'),
    ('1.8.1', 'B26', u'Эпидемический паротит'),
    ('1.8.2', 'B27', u'Инфекционный мононуклеоз'),
    ('1.9', 'B35-B49', u'Микозы'),
    ('1.10', 'B50-B64', u'Протозойные болезни'),
    ('1.11', 'B65-B83', u'Гельминтозы'),
    ('1.12', 'B90-B94', u'Последствия инфекционных и паразитарных болезней'),
    ('2', 'C00-D48', u'Новообразования'),
    ('2.1', 'C00-C97', u'Злокачественные новообразования'),
    ('2.1.1', 'C81-C96', u'Злокачественные новообразования лимфоидной,кроветворной и родственных им тканей'),
    ('2.2', 'D10-D36', u'Доброкачественные новообразования'),
    ('3', 'D50-D89', u'Болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм'),
    ('3.1', 'D50-D53', u'Анемии, связанные с питанием'),
    ('3.1.1', 'D50', u'Железодефицитная анемия'),
    ('3.2', 'D55-D59', u'Анемии вследствие ферментных нарушений'),
    ('3.3', 'D60-D64', u'Апластические и другие анемии'),
    ('3.4', 'D65-D69', u'Нарушения свертываемости крови, пурпура и другие геморрагические состояния'),
    ('3.4.1', 'D65', u'Диссеминированное внутрисосудистое свертывание [синдром дефибринации]'),
    ('3.5', 'D70-D77', u'Другие болезни крови и кроветворных органов'),
    ('3.6', 'D80-D89', u'Отдельные нарушения, вовлекающие иммунный механизм'),
    ('4', 'E00-E90', u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ'),
    ('4.1', 'E00-E07', u'Болезни щитовидной железы'),
    ('4.1.1', 'E05', u'Тиреотоксикоз [гипертиреоз]'),
    ('4.2', 'E10-E14', u'Сахарный диабет'),
    ('4.2.1', 'E10', u'Инсулинозависимый сахарный диабет'),
    ('4.2.2', 'E11', u'Инсулиннезависимый сахарный диабет'),
    ('4.3', 'E20-E35', u'Нарушения других эндокринных желез'),
    ('4.4', 'E40-E46', u'Недостаточность питания'),
    ('4.4.1', 'E43', u'Тяжелая белково-энергетическая недостаточность неуточненная'),
    ('4.4.2', 'E44.0', u'Умеренная белково-энергетическая недостаточность'),
    ('4.4.3', 'E44.1', u'Легкая белково-энергетическая недостаточность'),
    ('4.5', 'E50-E64', u'Другие виды недостаточности питания'),
    ('4.5.1', 'E55.0', u'Рахит активный'),
    ('4.5.2', 'E64.3', u'Последствия рахита'),
    ('4.6', 'E66', u'Ожирение'),
    ('4.7', 'E70-E90', u'Нарушения обмена веществ'),
    ('4.7.1', 'E70.0', u'Классическая фенилкетонурия'),
    ('4.7.2', 'E83.3', u'Нарушения обмена фосфора'),
    ('4.7.3', 'E84', u'Кистозный фиброз'),
    ('4.7.4', 'E77.8, E79, E83.5, E74.9', u'Другие нарушения обмена веществ (обмен. нефропатия)'),
    ('5', 'F00-F99', u'Психические расстройства и расстройства поведения'),
    ('5.1', 'F40-F48', u'Невротические, связанные со стрессом и соматоформные расстройства'),
    ('5.2', 'F80-F90', u'Расстройства психологического развития'),
    ('5.3', 'F95', u'Тики'),
    ('5.4', 'F98.0', u'Энурез неорганической природы'),
    ('5.5', 'F98.1', u'Энкопрез неорганической природы'),
    ('5.6', 'F98.5', u'Заикание [запинание]'),
    ('6', 'G00-G99', u'Болезни нервной системы'),
    ('6.1', 'G00-G09', u'Воспалительные болезни центральной нервной системы'),
    ('6.1.1', 'G09', u'Последствия воспалительных болезней центральной нервной системы'),
    ('6.2', 'G40-G41', u'Эпилепсия'),
    ('6.3', 'G50-G59', u'Поражения отдельных нервов, нервных корешков и сплетений'),
    ('6.4', 'G70-G73', u'Болезни нервно-мышечного синапса и мышц'),
    ('6.5', 'G80', u'Детский церебральный паралич'),
    ('6.6', 'G90.9', u'Расстройство вегетативной [автономной] нервной системы неуточненное'),
    ('6.7', 'G94.8', u'Другие уточненные поражения головного мозга при болезнях, классифицированных в других рубриках'),
    ('7', 'H00-H59', u'Болезни глаза и его придаточного аппарата'),
    ('7.1', 'H49-H50', u'Болезни мышц глаза, нарушения содружественного движения глаз, косоглазие'),
    ('7.2', 'H52', u'Нарушения рефракции и аккомодации'),
    ('7.2.1', 'H52.1', u'Миопия'),
    ('7.3', 'H53-H54', u'Зрительные расстройства и слепота'),
    ('8', 'H60-H95', u'Болезни уха и сосцевидного отростка'),
    ('8.1', 'H65.0, H65.1, H65.9, H66.0', u'Острый отит'),
    ('8.2', 'H65.2-H65.4, H66.1-H66.4, H66.9', u'Хронический отит'),
    ('8.3', 'H90-H91', u'Потеря слуха (глухота)'),
    ('9', 'I00-I99', u'Болезни системы кровообращения'),
    ('9.1', 'I00-I02', u'Острая ревматическая лихорадка'),
    ('9.2', 'I05-I09', u'Хронические ревматические болезни сердца'),
    ('9.2.1', 'I05-I08', u'Болезни клапанов'),
    ('9.3', 'I10-I15', u'Болезни, характеризующиеся повышенным кровяным давлением'),
    ('9.3.1', 'I10', u'Эссенциальная [первичная] гипертензия'),
    ('9.4', 'I30-I52', u'Другие болезни сердца'),
    ('10', 'J00-J99', u'Болезни органов дыхания'),
    ('10.1', 'J00-J06', u'Острые респираторные инфекции верхних дыхательных путей'),
    ('10.1.1', 'J03', u'Острый тонзиллит'),
    ('10.2', 'J10-J11', u'Грипп и пневмония'),
    ('10.3', 'J12-J18', u'Пневмония'),
    ('10.4', 'J20-J22', u'Другие острые респираторные инфекции нижних дыхательных путей'),
    ('10.5', 'J30-J39', u'Другие болезни верхних дыхательных путей'),
    ('10.5.1', 'J30.1', u'Аллергический ринит, вызванный пыльцой растений'),
    ('10.5.2', 'J31.1, J31.2, J32                   ', u'Хронический фарингит, назофарингит, синусит'),
    ('10.6', 'J40-J43', u'Бронхит и эмфизема'),
    ('10.7', 'J45-J46', u'Астма, астматический статус'),
    ('10.8', 'J44, J47', u'Другие хронические обструктивные легочные болезни, бронхоэктатическая болезнь'),
    ('10.9', 'J84-J94', u'Другие болезни органов дыхания'),
    ('11', 'K00-K93', u'Болезни органов пищеварения'),
    ('11.1', 'K20-K23', u'Болезни пищевода'),
    ('11.2', 'K25-K26', u'Язва желудка и язва двенадцатиперстной кишки'),
    ('11.3', 'K29.0, K29.1', u'Острый гастрит'),
    ('11.4', 'K29.3-K29.9', u'Хронический гастрит, дуоденит и гастродуоденит'),
    ('11.5', 'K30-K31', u'Функциональные расстройства желудка и язва двенадцатиперстной кишки'),
    ('11.6', 'K35', u'Острый аппендицит'),
    ('11.7', 'K40-K46', u'Грыжи брюшной полости'),
    ('11.8', 'K50-K52', u'Неинфекционный энтерит и колит'),
    ('11.9', 'K55-K63', u'Другие болезни кишечника'),
    ('11.10', 'K73', u'Хронический гепатит, не классифицированный в других рубриках'),
    ('11.11', 'K80', u'Желчнокаменная болезнь [холелитиаз]'),
    ('11.12', 'K81.0, K81.1', u'Острый холецистит и хронический холецистит'),
    ('11.13', 'K82.8, K83', u'Дискенизии желчевыводящих путей, другие болезни желчевыводящих путей'),
    ('11.14', 'K85-K86', u'Болезни поджелудочной железы'),
    ('11.15', 'K90-K93', u'Другие болезни органов пищеварения'),
    ('11.15.1', 'K90.0', u'Целиакия'),
    ('12', 'L00-L99', u'Болезни кожи и подкожной клетчатки'),
    ('12.1', 'L00-L08', u'Инфекции кожи и подкожной клетчатки'),
    ('12.2', 'L20', u'Атопический дерматит'),
    ('12.3', 'L23-L25', u'Контактный дерматит'),
    ('13', 'M00-M99', u'Болезни костно-мышечной системы и соединительной ткани'),
    ('13.1', 'M00-M03', u'Инфекционные артропатии'),
    ('13.2', 'M05-M14', u'Воспалительные полиартропатии'),
    ('13.2.1', 'M05-M06', u'Ревматоидный артрит'),
    ('13.2.2', 'M08', u'Юношеский [ювенильный] артрит'),
    ('13.3', 'M30-M36', u'Системные поражения соединительной ткани'),
    ('13.4', 'M40-M54', u'Дорсопатии'),
    ('13.4.1', 'M41', u'Сколиоз'),
    ('13.4.2', 'M42', u'Остеохондроз позвоночника'),
    ('13.5', 'M80-M94', u'Остеопатии, хондропатии'),
    ('13.5.1', 'M86', u'Остеомиелит'),
    ('13.6', 'M65-M68', u'Поражения синовиальных оболочек и сухожилий'),
    ('14', 'N00-N99', u'Болезни мочеполовой системы'),
    ('14.1', 'N00-N08', u'Гломерулярные болезни'),
    ('14.1.1', 'N00-N01', u'Острый нефрит'),
    ('14.1.2', 'N03', u'Хронический нефритический синдром'),
    ('14.2', 'N10-N16', u'Тубулоинтерстициальные болезни почек'),
    ('14.2.1', 'N10', u'Острый тубулоинтерстициальный нефрит'),
    ('14.2.2', 'N11', u'Хронический тубулоинтерстициальный нефрит'),
    ('14.3', 'N17-N19', u'Почечная недостаточность'),
    ('14.4', 'N20', u'Камни почки и мочеточника'),
    ('14.5', 'N25-N29', u'Другие болезни почки и мочеточника'),
    ('14.6', 'N30-N39', u'Другие болезни мочевыделительной системы'),
    ('14.6.1', 'N30.0, N30.1', u'Острый и хронический цистит'),
    ('14.7', 'N40-N51', u'Болезни мужских половых органов'),
    ('14.8', 'N70-N77', u'Воспалительные болезни женских тазовых органов'),
    ('14.8.1', 'N76', u'Другие воспалительные болезни влагалища и вульвы'),
    ('14.9', 'N91, N92', u'Нарушения менструального цикла'),
    ('16', 'P00-P96', u'Заболевания перинатального периода'),
    ('16.1', 'P10-P15', u'Родовая травма'),
    ('16.1.1', 'P10.0', u'Субдуральное кровоизлияние при родовой травме'),
    ('16.1.2', 'P10.1', u'Кровоизлияние в мозг при родовой травме'),
    ('16.1.3', 'P11.5', u'Повреждение позвоночника и спинного мозга при родовой травме'),
    ('16.2', 'P05', u'Замедленный рост и недостаточность питания плода'),
    ('16.3', 'P20-P21', u'Внутриутробная гипоксия и асфиксия при родах'),
    ('16.4', 'P22.0', u'Синдром дыхательного расстройства у новорожденного'),
    ('16.5', 'P23', u'Врожденная пневмония'),
    ('16.6', 'P35-P39', u'Инфекционные болезни, специфичные для перинатального периода'),
    ('16.6.1', 'P36', u'Бактериальный сепсис новорожденного'),
    ('16.6.2', 'P38', u'Омфалит новорожденного с небольшим кровотечением или без него'),
    ('16.6.3', 'P39.0', u'Неонатальный инфекционный мастит'),
    ('16.6.4', 'P39.1', u'Конъюнктивит и дакриоцистит у новорожденного'),
    ('16.6.5', 'P35, P37', u'Другие врожденные инфекционные болезни'),
    ('16.7', 'P50-P61', u'Геморрагические и гематологические нарушения у плода и новорожденного'),
    ('16.7.1', 'P52.0-P52.3', u'Внутрижелудочковое кровоизлияние'),
    ('16.7.2', 'P52.5', u'Субарахноидальное (нетравматическое) кровоизлияние у плода и новорожденного'),
    ('16.8', 'P55', u'Гемолитическая болезнь плода и новорожденного'),
    ('16.9', 'P57-P59', u'Другие желтухи перинатального периода'),
    ('16.10', 'P60-P96', u'Другие болезни перинатального периода'),
    ('16.10.1', 'P91', u'Энцефалопатия перинатального периода'),
    ('17', 'Q00-Q99', u'Врожденные аномалии, деформации и хромосомные нарушения'),
    ('17.1', 'Q00-Q07', u'Врожденные аномалии [пороки развития] нервной системы'),
    ('17.2', 'Q10-Q18', u'Врожденные аномалии глаза, уха, лица и шеи'),
    ('17.3', 'Q20-Q28', u'Врожденные аномалии [пороки развития] системы кровообращения'),
    ('17.3.1', 'Q20-Q24', u'Врожденные аномалии камер сердца и соединений'),
    ('17.3.2', 'Q25-Q26', u'Врожденные аномалии сосудов'),
    ('17.4', 'Q30-Q34', u'Врожденные аномалии [пороки развития] органов дыхания'),
    ('17.5', 'Q35-Q37', u'Расщелина губы и неба [заячья губа и волчья пасть]'),
    ('17.6', 'Q38-Q45', u'Другие врожденные аномалии [пороки развития] органов пищеварения'),
    ('17.7', 'Q50-Q56', u'Врожденные аномалии [пороки] половых органов'),
    ('17.8', 'Q60-Q64', u'Врожденные аномалии [пороки развития] мочевой системы'),
    ('17.9', 'Q65-Q79', u'Врожденные аномалии [пороки развития] и деформации костно-мышечной системы'),
    ('17.10', 'Q80-Q89', u'Другие врожденные аномалии [пороки развития]'),
    ('17.11', 'Q90-Q99', u'Хромосомные аномалии, не классифицированные в других рубриках'),
    ('17.11.1', 'Q90', u'Синдром Дауна'),
    ('18', 'R00-R99', u'Симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях'),
    ('18.1', 'R01', u'Сердечные шумы и другие сердечные звуки'),
    ('18.2', 'R56', u'Судороги, не классифицированные в других рубриках'),
    ('19', 'S00-T98', u'Травмы, отравления и некоторые другие последствия воздействия внешних причин'),
    ('19.1', 'T90-T98', u'Последствия травм, отравлений и других воздействий внешних причин'),
]

def selectData(registeredInPeriod, begDate, endDate, eventPurposeIdList, eventTypeId, orgStructureId, personId, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, areaIdEnabled, areaId, locality):
    stmt="""
SELECT
   Diagnosis.MKB AS MKB,
   COUNT(*) AS sickCount,
   (%s) AS firstInPeriod,
   IF((SELECT MAX(rbDispanser.observed)
FROM
Diagnostic AS D1
LEFT JOIN rbDispanser ON rbDispanser.id = D1.dispanser_id
WHERE
  D1.diagnosis_id = Diagnosis.id
  AND D1.endDate = (
    SELECT MAX(D2.endDate)
    FROM Diagnostic AS D2
    WHERE D2.diagnosis_id = Diagnosis.id
      AND D2.dispanser_id IS NOT NULL
      AND  D2.endDate<%s))
      = 1, 1, 0) AS observed

FROM Diagnosis
LEFT JOIN Client ON Client.id = Diagnosis.client_id
LEFT JOIN ClientAddress ON ClientAddress.client_id = Diagnosis.client_id
                        AND ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=1 and CA.client_id = Diagnosis.client_id)
LEFT JOIN Address ON Address.id = ClientAddress.address_id
LEFT JOIN rbDiagnosisType    ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
WHERE %s
GROUP BY MKB, firstInPeriod, observed
    """
    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].lt(endDate.addDays(1))]))
    cond.append(db.joinOr([tableDiagnosis['endDate'].ge(begDate), tableDiseaseCharacter['code'].eq('3')]))

    diagnosticQuery = tableDiagnostic
    diagnosticCond = [ tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']),
                       tableDiagnostic['deleted'].eq(0)
                     ]
    if registeredInPeriod:
        addDateInRange(diagnosticCond, tableDiagnostic['setDate'], begDate, endDate)
    if personId:
        diagnosticCond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if eventTypeId:
        tableEvent = db.table('Event')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        diagnosticCond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIdList:
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        diagnosticQuery = diagnosticQuery.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        diagnosticCond.append(tableEventType['purpose_id'].inlist(eventPurposeIdList))
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')
    if areaIdEnabled:
        if areaId:
            orgStructureIdList = getOrgStructureDescendants(areaId)
        else:
            orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        cond.append(db.existsStmt(tableOrgStructureAddress, subCond))
    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    return db.query(stmt % (db.joinAnd([tableDiagnosis['setDate'].le(endDate),
                                        tableDiagnosis['setDate'].ge(begDate)]),
                            tableDiagnosis['setDate'].formatValue(endDate.addDays(1)),
                            db.joinAnd(cond)))


class CStatReportF71(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сводная ведомость учёта заболеваний (71 форма)')


    def getDefaultParams(self):
        result = CReport.getDefaultParams(self)
        result['ageFrom']     = 0
        result['ageTo']       = 14
        return result


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setAreaEnabled(True)
#        result.setMKBFilterEnabled(True)
#        result.setAccountAccompEnabled(False)
        result.setTitle(self.title())
        return result


    def build(self, params):
        registeredInPeriod = params.get('registeredInPeriod', False)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeIdList = params.get('eventPurposeIdList', [])
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        areaIdEnabled = params.get('areaIdEnabled', None)
        areaId = params.get('areaId', None)
        locality = params.get('locality', 0)
        query = selectData(registeredInPeriod, begDate, endDate, eventPurposeIdList, eventTypeId, orgStructureId, personId, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, areaIdEnabled, areaId, locality)
        mapRows = createMapCodeToRowIdx([row[1] for row in Rows])
        rowSize = 3
        reportData = [ [0]*rowSize for row in xrange(len(Rows)) ]

        while query.next():
            record    = query.record()
            MKB       = normalizeMKB(forceString(record.value('MKB')))
            sickCount = forceInt(record.value('sickCount'))
            firstInPeriod = forceBool(record.value('firstInPeriod'))
            observed = forceBool(record.value('observed'))

            cols = [0]
            if firstInPeriod:
                cols.append(1)
            if observed:
                cols.append(2)

            for row in mapRows.get(MKB, []):
                reportLine = reportData[row]
                for col in cols:
                    reportLine[col] += sickCount

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'№ строки',      ], CReportBase.AlignLeft),
            ('45%', [u'Наименование',  ], CReportBase.AlignLeft),
            ('10%', [u'код МКБ',       ], CReportBase.AlignLeft),
            ('10%', [u'Всего',         ], CReportBase.AlignRight),
            ('10%', [u'В т.ч. впервые' ], CReportBase.AlignRight),
            ('10%', [u'Состоит на д.н. на конец периода'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)

        for row, rowDescr in enumerate(Rows):
            reportLine = reportData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 2, rowDescr[1])
            table.setText(i, 1, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])

        return doc
