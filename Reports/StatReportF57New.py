# coding=utf-8
from PyQt4 import QtCore
from PyQt4 import QtGui

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from library.Utils import forceString, forceInt
from Reports.Ui_StatReportF57NewSetup import Ui_StatReportF57NewSetupDialog

# Список кодов МКБ, означающих ДТП (расшифровка регулярного выражения):
# V(01-04, 06).1
# V(10-29).(4-9)
# V(30-38, 40-48, 50-58, 60-68, 70-78).(5-9)
# V(39, 49, 59, 69, 79).(4-9)
# V82.(1, 9)
# V(83-86).(0-3)
# V87.(0-9)
# V89.(2-3)
ROAD_ACCIDENT_REGEXP = ur'(' \
                       ur'V0[1-46]\.1' \
                       ur'|' \
                       ur'V[1-2][0-9]\.[4-9]' \
                       ur'|' \
                       ur'V[3-7][0-8]\.[5-9]' \
                       ur'|' \
                       ur'V[3-7]9\.[4-9]' \
                       ur'|' \
                       ur'V82\.[19]' \
                       ur'|' \
                       ur'V8[3-6]\.[0-3]' \
                       ur'|' \
                       ur'V87\.[0-9]' \
                       ur'|' \
                       ur'V89\.[2-3]' \
                       ur'|' \
                       ur'V09\.[23]' \
                       ur').*'

REPORT_1000 = 0
REPORT_2000 = 1
REPORT_3000 = 2
REPORT_3500 = 3

AGE_FILTERS = {
    REPORT_1000: 'age(c.birthDate, e.setDate) < 18',
    REPORT_2000: 'age(c.birthDate, e.setDate) >= 18',
    REPORT_3000: 'c.sex = 1 AND age(c.birthDate, e.setDate) >= 60 OR c.sex = 2 AND age(c.birthDate, e.setDate) >= 55'
}


def genMKBExpr(start, end=None, field='d.MKB', end99=True):
    if end99:
        if end:
            return u"%(f)s >= '%(s)s' AND %(f)s <= '%(e)s.99'" % {'s': start, 'e': end, 'f': field}
        else:
            return u"%(f)s >= '%(s)s' AND %(f)s <= '%(s)s.99'" % {'s': start, 'f': field}
    else:
        return u"%(f)s >= '%(s)s' AND %(f)s <= '%(e)s'" % {'s': start, 'e': end, 'f': field}


# rows: (name, displayRange, queryRange, hierarchyLevel)
rows = (
    (u'Всего, из них:', u'S00-T98', genMKBExpr('S00', 'T98'), 0),
    (u'травмы головы, всего', u'S00-S09', genMKBExpr('S00', 'S09'), 1),
    (u'&nbsp;из них:<br/>перелом черепа и лицевых костей', u'S02', genMKBExpr('S02'), 2),
    (u'травма глаза и глазницы', u'S05', genMKBExpr('S05'), 2),
    (u'внутричерепная травма', u'S06', genMKBExpr('S06'), 2),
    (u'травмы шеи, всего', u'S10-S19', genMKBExpr('S10', 'S19'), 1),
    (u'&nbsp;из них:<br/>перелом шейного отдела позвоночника', u'S12', genMKBExpr('S12'), 2),
    (u'травма нервов и спинного мозга на уровне шеи', u'S14', genMKBExpr('S14'), 2),
    (u'травмы грудной клетки, всего', u'S20-S29', genMKBExpr('S20', 'S29'), 1),
    (u'&nbsp;из них:<br/>перелом ребра (ребер), грудины и грудного отдела позвоночника', u'S22', genMKBExpr('S22'), 2),
    (u'травма сердца', u'S26', genMKBExpr('S26'), 2),
    (u'травма других и неуточненных органов грудной полости', u'S27', genMKBExpr('S27'), 2),
    (u'травмы живота, нижней части спины, поясничного отдела позвоночника и таза, всего',
     u'S30-S39', genMKBExpr('S30', 'S39'), 1),
    (u'&nbsp;из них:<br/>перелом пояснично-крестцового отдела позвоночника и костей таза',
     u'S32', genMKBExpr('S32'), 2),
    (u'травма органов брюшной полости', u'S36', genMKBExpr('S36'), 2),
    (u'травма тазовых органов', u'S37', genMKBExpr('S37'), 2),
    (u'травмы плечевого пояса и плеча, всего', u'S40-S49', genMKBExpr('S40', 'S49'), 1),
    (u'&nbsp;из них:<br/>перелом на уровне плечевого пояса и плеча', u'S42', genMKBExpr('S42'), 2),
    (u'травмы локтя и предплечья, всего', u'S50-S59', genMKBExpr('S50', 'S59'), 1),
    (u'&nbsp;из них:<br/>перелом костей предплечья', u'S52', genMKBExpr('S52'), 2),
    (u'травмы запястья и кисти, всего', u'S60-S69', genMKBExpr('S60', 'S69'), 1),
    (u'&nbsp;из них:<br/>перелом на уровне запястья и кисти', u'S62', genMKBExpr('S62'), 2),
    (u'травмы области тазобедренного сустава и бедра, всего', u'S70-S79', genMKBExpr('S70', 'S79'), 1),
    (u'&nbsp;из них:<br/>перелом бедренной кости', u'S72', genMKBExpr('S72'), 2),
    (u'травмы колена и голени, всего', u'S80-S89', genMKBExpr('S80', 'S89'), 1),
    (u'&nbsp;из них:<br/>перелом костей голени, включая голеностопный сустав', u'S82', genMKBExpr('S82'), 2),
    (u'травмы области голеностопного сустава и стопы, всего', u'S90-S99', genMKBExpr('S90', 'S99'), 1),
    (u'&nbsp;из них:<br/>перелом стопы, исключая перелом голеностопного сустава', u'S92', genMKBExpr('S92'), 2),
    (u'травмы, захватывающие несколько областей тела, всего', u'T00-T07', genMKBExpr('T00', 'T07'), 1),
    (u'&nbsp;из них:<br/>переломы, захватывающие несколько областей тела', u'T02', genMKBExpr('T02'), 2),
    (u'травмы неуточненной части туловища, конечности или области тела', u'T08-T14', genMKBExpr('T08', 'T14'), 1),
    (u'последствия проникновения инородного тела через естественные отверстия',
     u'T15-T19', genMKBExpr('T15', 'T19'), 1),
    (u'термические и химические ожоги', u'T20-T32', genMKBExpr('T20', 'T32'), 1),
    (u'отморожение', u'T33-T35', genMKBExpr('T33', 'T35'), 1),
    (u'отравление лекарственными средствами, медикаментами и биологическими веществами, всего',
     u'T33-T35', genMKBExpr('T33', 'T35'), 1),
    (u'&nbsp;из них:<br/>отравление наркотиками', u'T40.0-6', genMKBExpr('T40', 'T40.6', end99=False), 2),
    (u'отравление психотропными средствами', u'T43', genMKBExpr('T43'), 2),
    (u'токсическое действие веществ, преимущественно немедицинского назначения, всего',
     u'T51-T65', genMKBExpr('T51', 'T65'), 1),
    (u'&nbsp;из них:<br/>токсическое действие алкоголя', u'T51', genMKBExpr('T51'), 2),
    (u'другие и неуточненные эффекты воздействия внешних причин', u'T66-T78', genMKBExpr('T66', 'T78'), 1),
    (u'осложнения хирургических и терапевтических вмешательств', u'T80-T88', genMKBExpr('T80', 'T88'), 1),
    (u'последствия травм, отравлений и других последствий внешних причин', u'T90-T98', genMKBExpr('T90', 'T98'), 1),
)

# rows: (name, displayRange, queryRange, hierarchyLevel, lineNumber)
overview_rows = (
    (u'Случаи смерти от всех внешних причин', u'V01-Y98', genMKBExpr('V01', 'Y98', 'd.MKBEx'), 0, '1'),
    (u'&nbsp;из них:<br/>Несчастные случаи, всего', u'V01-X59', genMKBExpr('V01', 'X59', 'd.MKBEx'), 1, '2'),
    (u'&nbsp;из них:<br/>транспортные', u'V01-V99', genMKBExpr('V01', 'V99', 'd.MKBEx'), 2, '2.1'),
    (u'&nbsp;из них:<br/>дорожно-транспортные', u'&lt;*&gt;', "d.MKBEx REGEXP '%s'" % ROAD_ACCIDENT_REGEXP, 3, '2.1.1'),
    (u'падения', u'W00-W19', genMKBExpr('W00', 'W19', 'd.MKBEx'), 2, '2.2'),
    (u'утопление', u'W65-W74', genMKBExpr('W65', 'W74', 'd.MKBEx'), 2, '2.3'),
    (u'с угрозой дыханию', u'W75-W84', genMKBExpr('W75', 'W84', 'd.MKBEx'), 2, '2.4'),
    (u'воздействие дыма, огня, пламени', u'X00-X09', genMKBExpr('X00', 'X09', 'd.MKBEx'), 2, '2.5'),
    (u'Самоубийства', u'X60-X84', genMKBExpr('X60', 'X84', 'd.MKBEx'), 1, '3'),
    (u'Убийства', u'X85-Y09', genMKBExpr('X85', 'Y09', 'd.MKBEx'), 1, '4'),
    (u'Повреждения с неопределенными намерениями', u'Y10-Y34', genMKBExpr('Y10', 'Y34', 'd.MKBEx'), 1, '5')
)

SINGLE_STMT = u'''
SELECT
  '%s' as groupName,
  '%s' as rangeMKB,
  COUNT(DISTINCT IF(d.MKBEx >= 'V01' AND d.MKBEx <= 'Y98.99', c.id , NULL)) as total,
  COUNT(DISTINCT IF(d.MKBEx >= 'V01' AND d.MKBEx <= 'V99.99', c.id , NULL)) as vehicleTotal,
  COUNT(DISTINCT IF(d.MKBEx REGEXP '%s', c.id , NULL)) as vehicleRoadAccident,
  COUNT(DISTINCT IF(d.MKBEx >= 'W00' AND d.MKBEx <= 'X59.99', c.id , NULL)) as otherTotal,
  COUNT(DISTINCT IF(d.MKBEx >= 'W65' AND d.MKBEx <= 'W74.99', c.id , NULL)) as otherDrowning,
  COUNT(DISTINCT IF(d.MKBEx >= 'X00' AND d.MKBEx <= 'X09.99', c.id , NULL)) as otherFire,
  COUNT(DISTINCT IF(d.MKBEx >= 'X40' AND d.MKBEx <= 'X49.99', c.id , NULL)) as otherPoisoning,
  COUNT(DISTINCT IF(d.MKBEx >= 'X42' AND d.MKBEx <= 'X42.99', c.id , NULL)) as otherDrugPoisoning,
  COUNT(DISTINCT IF(d.MKBEx >= 'X45' AND d.MKBEx <= 'X45.99', c.id , NULL)) as otherAlcoholPoisoning,
  COUNT(DISTINCT IF(d.MKBEx >= 'X60' AND d.MKBEx <= 'X84.99', c.id , NULL)) as selfHurtTotal,
  COUNT(DISTINCT IF(d.MKBEx >= 'X62' AND d.MKBEx <= 'X62.99', c.id , NULL)) as selfHurtDrug,
  COUNT(DISTINCT IF(d.MKBEx >= 'X65' AND d.MKBEx <= 'X65.99', c.id , NULL)) as selfHurtAlcohol,
  COUNT(DISTINCT IF(d.MKBEx >= 'X85' AND d.MKBEx <= 'Y09.99', c.id , NULL)) as attack,
  COUNT(DISTINCT IF(d.MKBEx >= 'Y10' AND d.MKBEx <= 'Y34.99', c.id , NULL)) as unknownIntent,
  COUNT(DISTINCT IF(d.MKBEx >= 'Y35' AND d.MKBEx <= 'Y38.99', c.id , NULL)) as lawful,
  COUNT(DISTINCT IF(d.MKBEx >= 'Y40' AND d.MKBEx <= 'Y84.99', c.id , NULL)) as medicalComplications,
  COUNT(DISTINCT IF(d.MKBEx >= 'Y85' AND d.MKBEx <= 'Y89.99', c.id , NULL)) as externalEffects
FROM Diagnosis d
  INNER JOIN Client c ON d.client_id = c.id AND c.deleted = 0
  INNER JOIN Event e ON c.id = e.client_id AND e.deleted = 0 AND e.execDate IS NOT NULL
WHERE
  d.deleted = 0 AND
  (%s) AND
  (%%(cond)s) AND
  (%%(data)s)
'''

OVERVIEW_SINGLE_STMT = u'''
SELECT
  '%s' as groupName,
  '%s' as rangeMKB,
  COUNT(DISTINCT IF(age(c.birthDate, e.setDate) < 18, c.id , NULL)) as children,
  COUNT(DISTINCT IF(age(c.birthDate, e.setDate) >= 18, c.id , NULL)) as grownups,
  COUNT(DISTINCT IF(c.sex = 1 AND age(c.birthDate, e.setDate) >= 60 OR c.sex = 2 AND age(c.birthDate, e.setDate) >= 55, c.id , NULL)) as elders
FROM Diagnosis d
  INNER JOIN Diagnostic di ON d.id = di.diagnosis_id
  INNER JOIN Client c ON d.client_id = c.id AND c.deleted = 0
  INNER JOIN Event e ON c.id = e.client_id AND di.event_id=e.id AND e.deleted = 0 AND e.execDate IS NOT NULL
  INNER JOIN EventType ON e.eventType_id = EventType.id AND EventType.deleted = 0
  INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
WHERE
  d.deleted = 0 AND
  rbEventTypePurpose.code = '5' AND
  d.MKB >= 'S00' AND d.MKB <= 'T98.99' AND
  (%s) AND
  (%%(cond)s) AND
  (%%(data)s)
'''


def prepareStmt(overview=False):
    if overview:
        # name, displayRange, queryRange
        return u'UNION'.join(OVERVIEW_SINGLE_STMT % (row[0], row[1], row[2]) for row in overview_rows)
    else:
        return u'UNION'.join(SINGLE_STMT % (row[0], row[1], ROAD_ACCIDENT_REGEXP, row[2]) for row in rows)


def selectData(age, start_date, end_date):
    db = QtGui.qApp.db
    data = []
    stmt = prepareStmt() % {'cond': db.joinAnd((
        AGE_FILTERS[age],
        'e.execDate BETWEEN \'%s\' AND \'%s\'' % (
            start_date.toString('yyyy-MM-dd'),
            end_date.toString('yyyy-MM-dd')
        )
        )),
        'data': 'd.setDate BETWEEN \'%s\' AND \'%s\'' % (
            start_date.toString('yyyy-MM-dd'),
            end_date.toString('yyyy-MM-dd')
        )}
    # print stmt
    query = db.query(stmt)
    while query.next():
        row = query.record()
        data.append({
            'groupName': forceString(row.value(0)),
            'rangeMKB': forceString(row.value(1)),
            'total': forceString(sum(forceInt(row.value(x)) for x in xrange(3, 19))),
            'vehicleTotal': forceString(row.value(3)),
            'vehicleRoadAccident': forceString(row.value(4)),
            'otherTotal': forceString(row.value(5)),
            'otherDrowning': forceString(row.value(6)),
            'otherFire': forceString(row.value(7)),
            'otherPoisoning': forceString(row.value(8)),
            'otherDrugPoisoning': forceString(row.value(9)),
            'otherAlcoholPoisoning': forceString(row.value(10)),
            'selfHurtTotal': forceString(row.value(11)),
            'selfHurtDrug': forceString(row.value(12)),
            'selfHurtAlcohol': forceString(row.value(13)),
            'attack': forceString(row.value(14)),
            'unknownIntent': forceString(row.value(15)),
            'lawful': forceString(row.value(16)),
            'medicalComplications': forceString(row.value(17)),
            'externalEffects': forceString(row.value(18)),
        })
    return stmt, data


def selectOverviewData(start_date, end_date):
    db = QtGui.qApp.db
    data = []
    stmt = prepareStmt(overview=True) % {
        'cond': 'e.execDate BETWEEN \'%s\' AND \'%s\'' % (
            start_date.toString('yyyy-MM-dd'),
            end_date.toString('yyyy-MM-dd')
        ),
        'data': 'd.setDate BETWEEN \'%s\' AND \'%s\'' % (
            start_date.toString('yyyy-MM-dd'),
            end_date.toString('yyyy-MM-dd')
        )
    }
    query = db.query(stmt)
    while query.next():
        row = query.record()
        data.append({
            'groupName': forceString(row.value(0)),
            'rangeMKB': forceString(row.value(1)),
            'children': forceString(row.value(2)),
            'grownups': forceString(row.value(3)),
            'elders': forceString(row.value(4)),
        })
    return stmt, data


def buildDetailed(age, start_date, end_date):
    tableColumns = (
        ('10%', [u'Травмы, отравления и некоторые другие последствия воздействия внешних причин (Класс XIX МКБ-10)', '', '', '', '', '1'], CReportBase.AlignCenter),
        ('5%', [u'Код по МКБ-10', '', '', '', '', '2'], CReportBase.AlignCenter),
        ('4%', [u'N строки', '', '', '', '', '3'], CReportBase.AlignCenter),
        ('5%', [u'Внешние причины заболеваемости и смертности (Класс XX МКБ-10)', u'Внешние причины заболеваемости и смертности, всего', '', '', 'V01-Y98', '4'], CReportBase.AlignCenter),
        ('5%', ['', u'Транспортные несчастные случаи (V01-V99)', u'Всего', '', 'V01-V99', '5'], CReportBase.AlignCenter),
        ('5%', ['', '', u'из них: дорожно-транспортные несчастные случаи', '', '<*>', '6'], CReportBase.AlignCenter),
        ('5%', ['', u'Другие внешние причины (W00-X59)', u'Всего', '', 'W00-X59', '7'], CReportBase.AlignCenter),
        ('5%', ['', '', u'из них:', u'случайное утопление', 'W65-W74', '8'], CReportBase.AlignCenter),
        ('5%', ['', '', '', u'воздействие дыма, огня и пламени', 'X00-X09', '9'], CReportBase.AlignCenter),
        ('5%', ['', '', '', u'случайное отравление', 'X40-X49', '10'], CReportBase.AlignCenter),
        ('4%', ['', '', u'из гр. 10:', u'наркотиками', 'X42', '11'], CReportBase.AlignCenter),
        ('4%', ['', '', '', u'алкоголем', 'X45', '12'], CReportBase.AlignCenter),
        ('5%', ['', u'Преднамеренное самоповреждение', u'Всего', '', 'X60-X84', '13'], CReportBase.AlignCenter),
        ('4%', ['', '', u'из них:', u'наркотиками', 'X62', '14'], CReportBase.AlignCenter),
        ('4%', ['', '', '', u'алкоголем', 'X65', '15'], CReportBase.AlignCenter),
        ('5%', ['', u'Нападение', '', '', 'X85-Y09', '16'], CReportBase.AlignCenter),
        ('5%', ['', u'Повреждение с неопределенными намерениями', '', '', 'Y10-Y34', '17'], CReportBase.AlignCenter),
        ('5%', ['', u'Действия, предусмотренные законом, военные операции и терроризм', '', '', 'Y35-Y38', '18'], CReportBase.AlignCenter),
        ('5%', ['', u'Осложнения терапевтических и хирургических вмешательств', '', '', 'Y40-Y84', '19'], CReportBase.AlignCenter),
        ('5%', ['', u'Последствия воздействия внешних причин заболеваемости и смертности', '', '', 'Y85-Y89', '20'], CReportBase.AlignCenter)
    )

    doc = QtGui.QTextDocument()
    cursor = QtGui.QTextCursor(doc)
    cursor.setCharFormat(CReportBase.ReportTitle)
    title = ''
    if age == REPORT_1000:
        title = u'Травмы по характеру и соответствующие им внешние причины у детей (0-17 лет включительно) (1000)'
    elif age == REPORT_2000:
        title = u'Травмы по характеру и соответствующие им внешние причины у взрослых (18 лет и более) (2000)'
    elif age == REPORT_3000:
        title = u'Травмы по характеру и соответствующие им внешние причины у взрослых старше трудоспособного ' \
                u'возраста (3000)'
    cursor.insertText(title)
    cursor.insertBlock()
    table = createTable(cursor, tableColumns)

    table.mergeCells(0, 0, 5, 1)
    table.mergeCells(0, 1, 5, 1)
    table.mergeCells(0, 2, 5, 1)
    table.mergeCells(0, 3, 1, 17)
    table.mergeCells(1, 3, 3, 1)
    table.mergeCells(1, 4, 1, 2)
    table.mergeCells(2, 4, 2, 1)
    table.mergeCells(2, 5, 2, 1)
    table.mergeCells(1, 6, 1, 6)
    table.mergeCells(2, 6, 2, 1)
    table.mergeCells(2, 7, 1, 3)
    table.mergeCells(2, 10, 1, 2)
    table.mergeCells(1, 12, 1, 3)
    table.mergeCells(2, 12, 2, 1)
    table.mergeCells(2, 13, 1, 2)
    table.mergeCells(1, 15, 3, 1)
    table.mergeCells(1, 16, 3, 1)
    table.mergeCells(1, 17, 3, 1)
    table.mergeCells(1, 18, 3, 1)
    table.mergeCells(1, 19, 3, 1)

    stmt, data = selectData(age, start_date, end_date)
    for i, row in enumerate(data):
        row_num = table.addRowWithHtmlContent(
            row['groupName'],
            row['rangeMKB'],
            str(i+1),
            row['total'],
            row['vehicleTotal'],
            row['vehicleRoadAccident'],
            row['otherTotal'],
            row['otherDrowning'],
            row['otherFire'],
            row['otherPoisoning'],
            row['otherDrugPoisoning'],
            row['otherAlcoholPoisoning'],
            row['selfHurtTotal'],
            row['selfHurtDrug'],
            row['selfHurtAlcohol'],
            row['attack'],
            row['unknownIntent'],
            row['lawful'],
            row['medicalComplications'],
            row['externalEffects']
        )
        cell = table.cellAt(row_num, 0)
        fmt = QtGui.QTextTableCellFormat()
        fmt.setLeftPadding(rows[i][3] * 10)  # hierarchyLevel
        cell.setFormat(fmt)

    return stmt, doc


def buildOverview(start_date, end_date):
    tableColumns = (
        ('40%', [u'Виды травм по внешней причине', u'', u'1'], CReportBase.AlignCenter),
        ('10%', [u'Коды по МКБ-10', u'', u'2'], CReportBase.AlignCenter),
        ('5%', [u'N строки', u'', u'3'], CReportBase.AlignCenter),
        ('15%', [u'Случаи смерти детей (0-17 лет включительно) (из таблицы 1000)', u'', u'4'], CReportBase.AlignCenter),
        ('15%', [u'Случаи смерти взрослых (18 лет и более) (из таблицы 2000)', u'', u'5'], CReportBase.AlignCenter),
        ('15%', [u'из гр. 5:', u'случаи смерти лиц старше трудоспособного возраста (из таблицы 3000)', u'6'], CReportBase.AlignCenter)
    )

    doc = QtGui.QTextDocument()
    cursor = QtGui.QTextCursor(doc)
    cursor.setCharFormat(CReportBase.ReportTitle)
    cursor.insertText(u'Случаи смерти от внешних причин (3500)')
    cursor.insertBlock()
    table = createTable(cursor, tableColumns)

    table.mergeCells(0, 0, 2, 1)
    table.mergeCells(0, 1, 2, 1)
    table.mergeCells(0, 2, 2, 1)
    table.mergeCells(0, 3, 2, 1)
    table.mergeCells(0, 4, 2, 1)

    stmt, data = selectOverviewData(start_date, end_date)
    for i, row in enumerate(data):
        row_num = table.addRowWithHtmlContent(
            row['groupName'],
            row['rangeMKB'],
            overview_rows[i][4],  # lineNumber
            row['children'],
            row['grownups'],
            row['elders'],
        )
        cell = table.cellAt(row_num, 0)
        fmt = QtGui.QTextTableCellFormat()
        fmt.setLeftPadding(overview_rows[i][3] * 10)  # hierarchyLevel
        cell.setFormat(fmt)
    return stmt, doc


class CStatReportF57New(CReport):
    def __init__(self, parent):
        super(CStatReportF57New, self).__init__(parent)
        self.setTitle(u'Сведения о травмах, отравлениях и некоторых других последствиях воздействия внешних причин '
                      u'(Ф57)')

    def getSetupDialog(self, parent):
        result = StatReportF57NewSetupDialog(parent)
        return result

    def build(self, params):
        t = params['reportType']
        doc = stmt = None
        if t == REPORT_3500:
            stmt, doc = buildOverview(params['dateFrom'], params['dateTo'])
        elif t in (REPORT_1000, REPORT_2000, REPORT_3000):
            stmt, doc = buildDetailed(t, params['dateFrom'], params['dateTo'])
        self.setQueryText(stmt)
        return doc


class StatReportF57NewSetupDialog(QtGui.QDialog, Ui_StatReportF57NewSetupDialog):
    def __init__(self, parent):
        super(StatReportF57NewSetupDialog, self).__init__(parent)
        self.setupUi(self)

    def setParams(self, params):
        self.cmbReportType.setCurrentIndex(params.get('reportType', 0))
        self.edtDateFrom.setDate(params.get('dateFrom', QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1)))
        self.edtDateTo.setDate(params.get('dateTo', QtCore.QDate().currentDate()))

    def params(self):
        return {
            'reportType': self.cmbReportType.currentIndex(),
            'dateFrom': self.edtDateFrom.date(),
            'dateTo': self.edtDateTo.date(),
        }
