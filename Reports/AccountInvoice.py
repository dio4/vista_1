# coding=utf-8
from PyQt4 import QtCore
from PyQt4 import QtGui

from Reports.ReportBase import CReportBase, createTable
from library.Utils import forceString, forceRef, forceInt


class CAccountInvoice:
    def __init__(self):
        pass

    def build(self, reps, pogrn, dats, datps, isOutArea, accountNumber, accName, payerCode):
        kd = 0
        amount = 0
        summ = 0

        for i in xrange(19):
            row = reps.get(i, {'eventSet': {}, 'tkd': 0, 'tsumm': 0})
            kd += row['tkd']
            amount += len(row['eventSet'])
            summ += row['tsumm']

        kd, amount, summ = str(kd), str(amount), str(summ)

        db = QtGui.qApp.db
        organisation = db.getRecord('Organisation', '*', QtGui.qApp.currentOrgId())

        tableOrganisation = db.table('Organisation')

        r = db.getRecordEx(tableOrganisation, [tableOrganisation['id'].name(), tableOrganisation['head_id'].name()],
                           [tableOrganisation['isInsurer'].eq(1),
                            tableOrganisation['deleted'].eq(0),
                            tableOrganisation['infisCode'].eq(payerCode)])

        payerId = None
        if r:
            payerId = forceRef(r.value('id'))

        # Определяем плательщика - тфомс или конкретная СМК
        if len(pogrn) == 1 and not isOutArea:
            ogrn = pogrn.keys()[0]
            record = db.getRecordEx(tableOrganisation,
                                    [tableOrganisation['id'].name(), tableOrganisation['head_id'].name()],
                                    [tableOrganisation['OGRN'].eq(ogrn),
                                     tableOrganisation['isInsurer'].eq(1),
                                     tableOrganisation['deleted'].eq(0),
                                     tableOrganisation['area'].eq('2300000000000')
                                     ]
                                    )
            if record:
                payerId = forceInt(record.value('id')) if not forceRef(record.value('head_id')) else forceInt(
                    record.value('head_id'))

        payer = db.getRecord('Organisation', '*', payerId)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        # header
        cursor.insertBlock(CReportBase.AlignCenter, CReportBase.TableHeader)
        cursor.insertText(u'СЧЁТ-ФАКТУРА ___ от %s\nИСПРАВЛЕНИЕ ___ от __________\n' % dats.toString('dd.MM.yyyy'))
        cursor.insertText(u'к реестру счетов № %s от %s за %s %s %s\n' % (
            forceString(accountNumber),
            dats.toString('dd.MM.yyyy'),
            datps.year(),
            QtCore.QDate().longMonthName(datps.month(), QtCore.QDate.StandaloneFormat),
            accName,
        ))

        # organisations info
        table = createTable(cursor, [], border=0)
        table.table.appendColumns(2)

        table.addRowWithContent(u'Продавец:', forceString(organisation.value('fullName')))
        table.addRowWithContent(u'Адрес:', forceString(organisation.value('Address')))
        table.addRowWithContent(u'ИНН/КПП продавца:',
                                forceString(organisation.value('INN')) + '/' + forceString(organisation.value('KPP')))
        table.addRowWithContent(u'Грузоотправитель и его адрес:', forceString(organisation.value('Address')))
        table.addRowWithContent(u'Грузополучатель и его адрес:', forceString(payer.value('Address')))
        table.addRowWithContent(u'К платежно-расчетному документу №:', u'')
        table.addRowWithContent(u'Покупатель:', forceString(payer.value('fullName')))
        table.addRowWithContent(u'Адрес:', forceString(payer.value('Address')))
        table.addRowWithContent(u'ИНН/КПП покупателя:',
                                forceString(payer.value('INN')) + '/' + forceString(payer.value('KPP')))
        table.addRowWithContent(u'Валюта: наименование, код:', u'Российский рубль, 383')

        cursor.movePosition(QtGui.QTextCursor.End)
        columns = (
            ('%30', [u'Наименование товара (описание выполненных работ, оказанных услуг), '
                     u'имущественного права'], CReportBase.AlignLeft),
            ('%30', [u'Единица измерения', u'код'], CReportBase.AlignCenter),
            ('%30', [u'', u'условное обозначение (национальное)'], CReportBase.AlignCenter),
            ('%30', [u'Количество (объем)'], CReportBase.AlignCenter),
            ('%30', [u'Цена (тариф) за единицу измерения'], CReportBase.AlignCenter),
            ('%30', [u'Стоимость товаров (работ, услуг), '
                     u'имущественных прав без налога - всего'], CReportBase.AlignCenter),
            ('%30', [u'В том числе сумма акциза'], CReportBase.AlignCenter),
            ('%30', [u'Налоговая ставка'], CReportBase.AlignCenter),
            ('%30', [u'Сумма налога, предъявляемая покупателю'], CReportBase.AlignCenter),
            ('%30', [u'Стоимость товаров (работ, услуг), '
                     u'имущественных прав с налогом - всего'], CReportBase.AlignCenter),
        )
        table = createTable(cursor, columns)
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)
        table.addRowWithContent('1', '2', '2a', '3', '4', '5', '6', '7', '8', '9')

        table.addRowWithContent(u'Сводный счет за пролеченных больных:\n- случаев лечения\n- кол-во койко-дней',
                                u'-', u'-',
                                amount + '\n' + kd,
                                u'-',
                                summ,
                                u'без акциза', u'без НДС', u'без НДС',
                                summ)
        row = table.addRowWithHtmlContent(u'<b><i>Всего к оплате:</i></b>', '', '', '', '', summ, '', '', '', summ)
        table.mergeCells(row, 0, 1, 5)
        table.mergeCells(row, 6, 1, 3)
        c = table.cellAt(3, 3)
        fmt = c.format()
        fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignBottom)
        c.setFormat(fmt)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'Главный врач __________ %s\t\tГл. бухгалтер __________ %s' % (
            forceString(organisation.value('chief')), forceString(organisation.value('accountant'))
        ))

        return doc

    def buildNew(self, reps, pogrn, dats, datps, isOutArea, accountNumber, accName, payerCode):
        db = QtGui.qApp.db
        organisation = db.getRecord('Organisation', '*', QtGui.qApp.currentOrgId())

        tableOrganisation = db.table('Organisation')

        r = db.getRecordEx(tableOrganisation, [tableOrganisation['id'].name(), tableOrganisation['head_id'].name()],
                           [tableOrganisation['isInsurer'].eq(1),
                            tableOrganisation['deleted'].eq(0),
                            tableOrganisation['infisCode'].eq(payerCode)])

        payerId = None
        if r:
            payerId = forceRef(r.value('id'))

        # Определяем плательщика - тфомс или конкретная СМК
        if len(pogrn) == 1 and not isOutArea:
            ogrn = pogrn.keys()[0]
            record = db.getRecordEx(tableOrganisation,
                                    [tableOrganisation['id'].name(), tableOrganisation['head_id'].name()],
                                    [tableOrganisation['OGRN'].eq(ogrn),
                                     tableOrganisation['isInsurer'].eq(1),
                                     tableOrganisation['deleted'].eq(0),
                                     tableOrganisation['area'].eq('2300000000000')
                                     ]
                                    )
            if record:
                payerId = forceInt(record.value('id')) if not forceRef(record.value('head_id')) else forceInt(
                    record.value('head_id'))

        payer = db.getRecord('Organisation', '*', payerId)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        # header
        cursor.insertBlock(CReportBase.AlignCenter, CReportBase.TableHeader)
        cursor.insertText(u'СЧЁТ-ФАКТУРА ___ от %s\nИСПРАВЛЕНИЕ ___ от __________\n' % dats.toString('dd.MM.yyyy'))
        cursor.insertText(u'к реестру счетов № %s от %s за %s %s %s\n' % (
            forceString(accountNumber),
            dats.toString('dd.MM.yyyy'),
            datps.year(),
            QtCore.QDate().longMonthName(datps.month(), QtCore.QDate.StandaloneFormat),
            accName,
        ))

        # organisations info
        table = createTable(cursor, [], border=0)
        table.table.appendColumns(2)

        table.addRowWithContent(u'Продавец:', forceString(organisation.value('fullName')))
        table.addRowWithContent(u'Адрес:', forceString(organisation.value('Address')))
        table.addRowWithContent(u'ИНН/КПП продавца:',
                                forceString(organisation.value('INN')) + '/' + forceString(organisation.value('KPP')))
        table.addRowWithContent(u'Грузоотправитель и его адрес:', forceString(organisation.value('Address')))
        table.addRowWithContent(u'Грузополучатель и его адрес:', forceString(payer.value('Address')))
        table.addRowWithContent(u'К платежно-расчетному документу №:', u'')
        table.addRowWithContent(u'Покупатель:', forceString(payer.value('fullName')))
        table.addRowWithContent(u'Адрес:', forceString(payer.value('Address')))
        table.addRowWithContent(u'ИНН/КПП покупателя:',
                                forceString(payer.value('INN')) + '/' + forceString(payer.value('KPP')))
        table.addRowWithContent(u'Валюта: наименование, код:', u'Российский рубль, 383')

        cursor.movePosition(QtGui.QTextCursor.End)
        columns = (
            ('%30', [u'Наименование товара (описание выполненных работ, оказанных услуг), '
                     u'имущественного права'], CReportBase.AlignLeft),
            ('%30', [u'Единица измерения', u'код'], CReportBase.AlignCenter),
            ('%30', [u'', u'условное обозначение (национальное)'], CReportBase.AlignCenter),
            ('%30', [u'Количество (объем)'], CReportBase.AlignCenter),
            ('%30', [u'Цена (тариф) за единицу измерения'], CReportBase.AlignCenter),
            ('%30', [u'Стоимость товаров (работ, услуг), '
                     u'имущественных прав без налога - всего'], CReportBase.AlignCenter),
            ('%30', [u'В том числе сумма акциза'], CReportBase.AlignCenter),
            ('%30', [u'Налоговая ставка'], CReportBase.AlignCenter),
            ('%30', [u'Сумма налога, предъявляемая покупателю'], CReportBase.AlignCenter),
            ('%30', [u'Стоимость товаров (работ, услуг), '
                     u'имущественных прав с налогом - всего'], CReportBase.AlignCenter),
            ('%30', [u'Страна происхождения товара', u'цифровой код'], CReportBase.AlignCenter),
            ('%30', [u'', u'краткое наименование'], CReportBase.AlignCenter),
            ('%30', [u'Номер таможенной декларации'], CReportBase.AlignCenter)
        )
        table = createTable(cursor, columns)
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)
        table.mergeCells(0, 10, 1, 2)
        table.mergeCells(0, 12, 2, 1)

        table.addRowWithContent('1', '2', '2a', '3', '4', '5', '6', '7', '8', '9', '10', '10a', '11')

        mainColumnTemplate = u'Подушевое финансирование по амбулаторно-поликлинической службе , %s'

        # Не пойдет, ключики отсортированы :(
        # for x in reps:
        #     table.addRowWithContent(
        #         mainColumnTemplate % x,
        #         u'792', u'чел',
        #         reps[x],  # amount
        #         '0', '0', '', '', '', '', '', '', ''
        #     )

        table.addRowWithContent(
            mainColumnTemplate % u'муж 0-1',
            u'792', u'чел',
            reps[u'муж 0-1']['count'],  # amount
            '0', forceString(reps[u'муж 0-1']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'жен 0-1',
            u'792', u'чел',
            reps[u'жен 0-1']['count'],  # amount
            '0', forceString(reps[u'жен 0-1']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'муж 1-4',
            u'792', u'чел',
            reps[u'муж 1-4']['count'],  # amount
            '0', forceString(reps[u'муж 1-4']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'жен 1-4',
            u'792', u'чел',
            reps[u'жен 1-4']['count'],  # amount
            '0', forceString(reps[u'жен 1-4']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'муж 5-17',
            u'792', u'чел',
            reps[u'муж 5-17']['count'],  # amount
            '0', forceString(reps[u'муж 5-17']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'жен 5-17',
            u'792', u'чел',
            reps[u'жен 5-17']['count'],  # amount
            '0', forceString(reps[u'жен 5-17']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'муж 18-59',
            u'792', u'чел',
            reps[u'муж 18-59']['count'],  # amount
            '0', forceString(reps[u'муж 18-59']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'жен 18-54',
            u'792', u'чел',
            reps[u'жен 18-54']['count'],  # amount
            '0', forceString(reps[u'жен 18-54']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'муж от 60',
            u'792', u'чел',
            reps[u'муж от 60']['count'],  # amount
            '0', forceString(reps[u'муж от 60']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )
        table.addRowWithContent(
            mainColumnTemplate % u'жен от 55',
            u'792', u'чел',
            reps[u'жен от 55']['count'],  # amount
            '0', forceString(reps[u'жен от 55']['total']),  # tariff & total sum
            '', '', '', '', '', '', ''
        )

        total = 0.0
        for x in reps:
            total += reps[x]['total']

        row = table.addRowWithHtmlContent(u'<b><i>Всего к оплате:</i></b>', '', '', '', '', forceString(total), '', '<center>X</center>', '', '0,00')
        table.mergeCells(row, 0, 1, 5)
        table.mergeCells(row, 6, 1, 3)
        table.mergeCells(row, 10, 1, 3)
        c = table.cellAt(3, 3)
        fmt = c.format()
        fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignBottom)
        c.setFormat(fmt)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock(CReportBase.AlignCenter)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock(CReportBase.AlignCenter)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'Главный врач __________ %s\t\tГл. бухгалтер __________ %s' % (
            forceString(organisation.value('chief')), forceString(organisation.value('accountant'))
        ))

        return doc
