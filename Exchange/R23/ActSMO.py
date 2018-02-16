# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

from PyQt4 import QtCore
from library.Utils import forceInt, forceString, monthNameGC
from ActsOfExprort import Act


AlignCenter = 'center'
AlignRight  = 'right'
AlignLeft   = 'left'

def createTableCol(value, align=AlignLeft):
        return '', [value], {'align': align}

def getFormat():
    return {'align': u'center'}

def insertText(text, align='left', format = u''):
    if text == u'\n' or u'':
        return insertBr()
    lines = text.split(u'\n')
    result = []
    for line in lines:
        result.append(insertLine(line, align, format))
    return u'\n'.join(result)

def insertLine(text, align='left', format = u''):
    result = []
    if text == u'\n' or u'':
        return insertBr()
    result.append(u'<p align="%s">' %align)
    result.append(text)
    result.append(u'</p>')
    return u''.join(result)

def insertBr():
    return u'<br/>'

def insertHr():
    return u'<hr color="black" height="1px", whidth="100%" noshade/>'


def insertTable(columns, format):
    table = [u'''<table width="100%">''']
    table.append(u'<tr>')
    for width, name in columns:
        table.append(u'<td width="%s">' %(forceString(width)))
        table.append(u'<p align=%s>' %format['align'])
        table.append(u'%s' %forceString(name))
        table.append(u'</p>')
        table.append(u'</td>')
    table.append(u'</tr>')
    table.append(u'</table>')
    return u'\n'.join(table)

def createTable(rows, format):
    html = [u'''<table width="100%" border="1" cellspacing="0" cellpadding="2" bordercolor="black">''']
    for row in rows:
        html.append(u'<tr>')
        for column in row:
            width = column[0]
            format_td = column[2] if len(column) > 2 else {}
            rowspan = format_td.get('rowspan', None)
            colspan = format_td.get('colspan', None)
            align = format_td.get('align', None)
            td = []
            td.append(u'<td width="%s"' %(forceString(width)))
            if rowspan:
                td.append(u'rowspan=%d' %rowspan)
            if colspan:
                td.append(u'colspan=%d' %colspan)
            if align:
                td.append(u'align=%s' %align)
            td.append(u'>')
            td.append(u'%s' % column[1][0])
            td.append(u'</td>')
            html.append(u' '.join(td))
        html.append(u'</tr>')
    html.append(u'</table>')
    return u'\n'.join(html)


class ActSMO(Act):

    def build(self, params):
        html = u'''
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
        <html>
            <head>
                <meta name="qrichtext" content="1" />
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <style type="text/css">
                    p, li { margin-top:0px;
                            margin-bottom:0px;
                            margin-left:0px;
                            margin-right:0px;
                            -qt-block-indent:0;
                            text-indent:0px;}
                    span {font-family:'Times'; font-size:10pt;}
                    hr { margin-top:2px;
                        margin-bottom:2px;}
                </style>
            </head>
            <body style=" font-family:'Times'; font-size:10pt; font-weight:400; font-style:normal;">
            '''

        date = params.get('date', QtCore.QDate())
        moOrgInfo = params.get('moOrgInfo', {})
        moOrgMainStuff = params.get('moOrgMainStuff', [u'\n', u'\n'])
        smoOrgInfo = params.get('smoOrgInfo', {})
        counters = params.get('prik', {}).get('codeMOCounters', {})
        body = []
        body.append(insertText(u'''ПРИЛОЖЕНИЕ № 1\nк совместному приказу министерства\nздравоохранения Краснодарского края\nи Территориального фонда обязательного\nмедицинского страхования Краснодарского края\nот 27.07.2015 Г. № 6217/225-П''', 'right'))
        body.append(insertText(u'''\n\n<<УТВЕРЖДЕНО ПРИЛОЖЕНИЕ № 2\nк приказу министерства здравоохранения\nКраснодарского края и Территориального фонда\nобязательного медицинского страхования Краснодарского края\nот 14.07.2015 Г. № 3914/163-П>>''', 'right'))
        body.append(insertText(u'''Акт\nсверки численности застрахованного населения к медицинской организации\nна «%d» %s %dг.\n\n''' %(date.day(), monthNameGC[date.month()], date.year()), 'center'))
        body.append(insertBr())
        body.append(insertText(smoOrgInfo.get('fullName', u'\n'), 'center'))
        body.append(insertHr())
        body.append(insertText(u'(наименование СМО)', 'center'))
        body.append(insertBr())
        body.append(insertTable([('20%', u'%s' %moOrgInfo.get('infisCode', u'\n')),
                                 ('80%', u'%s' %moOrgInfo.get('fullName', u'\n'))], getFormat()))
        body.append(insertHr())
        body.append(insertTable([('20%', u'(код МО)'),
                                 ('80%', u'(наименование МО)')], getFormat()))
        body.append(insertBr())

        tableColumns = \
        [
            [
                ('6%',  [u'№ п/п'], {'align': AlignCenter, 'rowspan': 3}),
                ('7%', [u'Код структурного подраделения'], {'align': AlignCenter, 'rowspan': 3}),
                ('19%', [u'Наименование структурного подразделения'], {'align': AlignCenter, 'rowspan': 3}),
                ('68%',  [u'Количество прикрепленного застрахованного населения, чел.'], {'align': AlignCenter, 'colspan': 11})
            ],
            [
                ('8%', [u'Всего'],{'align': AlignCenter, 'rowspan': 2}),
                ('60%',  [u'из них'], {'align': AlignCenter, 'colspan': 10}),
            ],
            [
                ('6%', [u'от 0-1 муж.'], {'align': AlignCenter}),
                ('6%', [u'от 0-1 жен.'], {'align': AlignCenter}),
                ('6%', [u'от 1-4 муж.'], {'align': AlignCenter}),
                ('6%', [u'от 1-4 жен.'], {'align': AlignCenter}),
                ('6%', [u'от 5-17 муж.'], {'align': AlignCenter}),
                ('6%', [u'от 5-17 жен.'], {'align': AlignCenter}),
                ('6%', [u'от 18-59 муж.'], {'align': AlignCenter}),
                ('6%', [u'от 18-54 жен.'], {'align': AlignCenter}),
                ('6%', [u'от 60 муж.'], {'align': AlignCenter}),
                ('6%', [u'от 55 жен.'], {'align': AlignCenter}),
            ],
        ]

        it = 1
        total = 0
        totals = {'Male': [0] * 5,
                  'Female': [0] * 5}
        defaultArray = [u'не указано'] * 5
        for code, counter in sorted(counters.items(), key=lambda x: forceInt(x[0])):
            sub_total = sum(counter.get('Male', []) + counter.get('Female', []))
            total += sub_total
            for key in totals.keys():
                totals[key] = map(lambda x, y: x+y, totals[key], counter.get(key, [0] * 5))
            tableRow = [createTableCol(it),
                        createTableCol(code),
                        createTableCol(counter.get('shortName', u'')),
                        createTableCol(sub_total, AlignCenter),
                        createTableCol(counter.get('Male', defaultArray)[0], AlignCenter),
                        createTableCol(counter.get('Female', defaultArray)[0], AlignCenter),
                        createTableCol(counter.get('Male', defaultArray)[1], AlignCenter),
                        createTableCol(counter.get('Female', defaultArray)[1], AlignCenter),
                        createTableCol(counter.get('Male', defaultArray)[2], AlignCenter),
                        createTableCol(counter.get('Female', defaultArray)[2], AlignCenter),
                        createTableCol(counter.get('Male', defaultArray)[3], AlignCenter),
                        createTableCol(counter.get('Female', defaultArray)[3], AlignCenter),
                        createTableCol(counter.get('Male', defaultArray)[4], AlignCenter),
                        createTableCol(counter.get('Female', defaultArray)[4], AlignCenter),
                        ]
            tableColumns.append(tableRow)
            it += 1

        totalRow = [('', [u'ИТОГО по медицинской организации'], {'align': AlignLeft, 'colspan': 3}),
                    createTableCol(total, AlignCenter),
                    createTableCol(totals.get('Male', defaultArray)[0], AlignCenter),
                    createTableCol(totals.get('Female', defaultArray)[0], AlignCenter),
                    createTableCol(totals.get('Male', defaultArray)[1], AlignCenter),
                    createTableCol(totals.get('Female', defaultArray)[1], AlignCenter),
                    createTableCol(totals.get('Male', defaultArray)[2], AlignCenter),
                    createTableCol(totals.get('Female', defaultArray)[2], AlignCenter),
                    createTableCol(totals.get('Male', defaultArray)[3], AlignCenter),
                    createTableCol(totals.get('Female', defaultArray)[3], AlignCenter),
                    createTableCol(totals.get('Male', defaultArray)[4], AlignCenter),
                    createTableCol(totals.get('Female', defaultArray)[4], AlignCenter),
                    ]
        tableColumns.append(totalRow)

        table = createTable(tableColumns, {'border': 1})
        body.append(table)
        body.append(insertBr())
        body.append(insertTable([('20%', u''),
                                 ('20%', u''),
                                 ('80%',  u'%s' %moOrgMainStuff[0])], getFormat()))

        body.append(insertHr())
        body.append(insertTable([('20%', u'(подпись)'),
                                 ('20%', u''),
                                 ('80%', u'(Ф.И.О. руководителя МО)')], getFormat()))
        body.append(insertLine(u'МП'))
        body.append(insertBr())

        body.append(insertTable([('20%', u''),
                                 ('20%', u''),
                                 ('80%', u'%s' %smoOrgInfo.get('chief', u'\n'))], getFormat()))

        body.append(insertHr())
        body.append(insertTable([('20%', u'(подпись)'),
                                 ('20%', u''),
                                 ('80%', u'(Ф.И.О. руководителя СМО)')], getFormat()))
        body.append(insertLine(u'МП'))


        html += u'\n'.join(body)
        html += u'''
            </body>
        </html>
        '''
        return html