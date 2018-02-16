# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

from PyQt4 import QtCore, QtGui
from library.Utils import monthNameGC
from Reports.ReportBase import CReportBase, createTable

class Act():
    def __init__(self):
        self.docText = u''

    def build(self, params):
        pass

    def updateTags(self, text): #так как в разных сборках почему то не импртирует тег <br />, и по-разному сохраняет теги
        text = text.replace(u'''<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Times'; font-size:10pt;"></p>''',
                     u'''<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Times'; font-size:10pt;"><br /></p>'''
                    )
        text = text.replace(u'''<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Times';"></p>''',
                            u'''<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Times';"><br /></p>''')
        text = text.replace(u'''<table''',
                     u'''<table width="100%"''') #иначе нельзя установить ширину всей таблицы относительно листа
        return text

    def toUtf(self):
        return self.updateTags(unicode(self.docText.toHtml("utf-8").toUtf8(), encoding="UTF-8"))

class ActMIAC(Act):

    def build(self, params):
        def translateType(record):
            if record[1] == 'N':
                return u'Числ. (%d,%d)' %(record[2], record[3])
            elif record[1] == 'C':
                return u'Симв. (%d)' %(record[2])
            elif record[1] == 'D':
                return u'Дата'
            return u''
        tabulation = u'           '
        date = params.get('date', QtCore.QDate())
        currentOrgInfo = params['currentOrgInfo']
        currentOrgMainStuff =  params['currentOrgMainStuff']

        doc = QtGui.QTextDocument()
        doc.setPageSize(QtCore.QSizeF(210.0, 297.0))
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(self.getFormatGeneral())
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'Акт приёма-передачи архивного файла', self.getFormatTitle())
        cursor.insertText(u'\nРегионального регистра приписного населения №__________', self.getFormatTitle())
        tableColumns = [
                ('50%', [u''], CReportBase.AlignLeft),
                ('50%', [u''], CReportBase.AlignRight),
                ]
        table = createTable(cursor, tableColumns, headerRowCount=0, border = 0, charFormat = self.getFormatGeneral())
        row = table.addRow()
        table.setText(row, 0,u'г. Краснодар', self.getFormatGeneral(), CReportBase.AlignLeft)
        table.setText(row, 1,u'%d %s %dг.' %(date.day(), monthNameGC[date.month()], date.year()), self.getFormatGeneral(), CReportBase.AlignRight)
        row = table.addRow()
        #table.setText(row, 0,u'                                                                                         '\
        #                     u'                                                                                         '\
        #                     u'                                                                                         ', self.getFormatGeneral())
        cursor.movePosition(cursor.End)
        cursor.insertText(u'%sГБУЗ МИАЦ, именуемое в дальнейшем «Получатель», в лице начальника Рубцовой Ирины Темировны, '
                          u'с одной стороны, и %s именуемое в дальнейшем «Медицинская организация» в лице главного врача %s '
                          u'с другой стороны, составили настоящий акт о том, что Медицинская организация передала, '
                          u'а Исполнитель принял и провёл предварительную проверку (без групповых контролей) архивного '
                          u'файла Регионального регистра прикрепленного населения в соответствии с приказом Министерства '
                          u'здравоохранения Краснодарского края и Территориального фонда обязательного медицинского '
                          u'страхования Краснодарского края от 13.07.2015г. №3904/161-П.' %(tabulation, currentOrgInfo['fullName'], currentOrgMainStuff[0]), self.getFormatGeneral())


        cursor.insertText(u'\n\n Файл %s содержит %d записей, получен %d %s %d г.' %(params['prik']['filename'], params['prik']['counter'], date.day(), monthNameGC[date.month()], date.year()), self.getFormatGeneral())
        tableColumns = [
                ('16%', [u'Имя поля'], CReportBase.AlignLeft),
                ('8%', [u'Тип'], CReportBase.AlignLeft),
                ('19%', [u'Название'], CReportBase.AlignLeft),
                ('47%', [u'Примечание'], CReportBase.AlignLeft),
                ('10%', [u'Количество незаполенных записей по полю'], CReportBase.AlignLeft),
                ]
        table = createTable(cursor, tableColumns, charFormat = self.getFormatTitle(), borderBrush=self.getBorderBrush())
        records = self.getPrikFieldsWithDesc()
        emptyFieldsCounter = params['prik'].get('emptyFieldsCounter', {})
        for record in records:
            row = table.addRow()
            fields = (
                record[0],
                translateType(record),
                record[-2],
                record[-1],
                emptyFieldsCounter.get(record[0:2], 0)
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val, self.getFormatGeneral())

        if params.get('lgota', {}):
            cursor.movePosition(cursor.End)
            cursor.insertText(u'\n\n Файл %s содержит %d записей, получен %d %s %d г.' %(params['lgota']['filename'], params['lgota']['counter'], date.day(), monthNameGC[date.month()], date.year()), self.getFormatGeneral())
            table = createTable(cursor, tableColumns, charFormat = self.getFormatTitle(), borderBrush=self.getBorderBrush())
            records = self.getLgotaFieldsWithDesc()
            emptyFieldsCounter = params['lgota'].get('emptyFieldsCounter', {})
            for record in records:
                row = table.addRow()
                fields = (
                    record[0],
                    translateType(record),
                    record[-2],
                    record[-1],
                    emptyFieldsCounter.get(record[0:2], 0)
                )
                for col, val in enumerate(fields):
                    table.setText(row, col, val, self.getFormatGeneral())

        cursor.movePosition(cursor.End)
        cursor.insertText(u'\n\n Файл %s содержит %d записей, получен %d %s %d г.' %(params['uch']['filename'], params['uch']['counter'], date.day(), monthNameGC[date.month()], date.year()), self.getFormatGeneral())
        table = createTable(cursor, tableColumns, charFormat = self.getFormatTitle(), borderBrush=self.getBorderBrush())
        records = self.getUchFieldsWithDesc()
        emptyFieldsCounter = params['uch'].get('emptyFieldsCounter', {})
        for record in records:
            row = table.addRow()
            fields = (
                record[0],
                translateType(record),
                record[-2],
                record[-1],
                emptyFieldsCounter.get(record[0:2], 0)
            )
            if record[0] == 'D_FAM':
                descrRow = row
            for col, val in enumerate(fields):
                table.setText(row, col, val, self.getFormatGeneral())
            description = u'Данные врача участковой службы (врач-терапевт участковый, врач-педиатр участковый, врач общей практики).' \
                          u'\n\nИли данные врача с типом должности "средний медицинский персонал" (фельдшер, акушерка).' \
                          u'\nПрименяется для жителей сельской местности, где по месту жительства население обслуживают фельдшер ФАП и участковый врач ЦРБ или участковой больницы.' \
                          u'\n\nДанные должны соответствовать сведениям из федерального регистра медицинских работников.'
        table.setText(descrRow, 3, description, self.getFormatGeneral())
        table.mergeCells(descrRow, 3, row - descrRow + 1, 1)
        cursor.movePosition(cursor.End)
        cursor.insertText(u'\n\n%sКоличество участков, к которым приписаны более 3000 человек %d. Причина наличия вышеназванных участков: ' %(tabulation, params['prik'].get('big_uch_counter', 0)), self.getFormatGeneral())
        cursor.insertText(u'\n%sПодписывая настоящий акт, Получатель и Медицинская организация понимают, что итоги '
                          u'групповой проверки проводимой Получателем в соответствии со Справочником «Результаты сверки '
                          u'прикрепленного населения» SPR64 могут отличаться от итогов предварительной проверки, '
                          u'проведённой Получателем при приёме архивных файлов от Медицинской организации.' %tabulation, self.getFormatGeneral())
        cursor.insertText(u'\n', self.getFormatGeneral())
        tableColumns = [
                ('40%', [u''], CReportBase.AlignLeft),
                ('20%', [u''], CReportBase.AlignLeft),
                ('40%', [u''], CReportBase.AlignLeft),
                ]
        table = createTable(cursor, tableColumns, border = 0, charFormat = self.getFormatTitle())
        row = table.addRow()
        table.setText(row, 0, u'Получатель', self.getFormatTitle(), CReportBase.AlignLeft)
        table.setText(row, 2, u'Медицинская организация', self.getFormatTitle(), CReportBase.AlignLeft)
        row = table.addRow()
        table.setText(row, 0, u'__________ / Рубцова И.Т. /', self.getFormatGeneral(), CReportBase.AlignLeft)
        table.setText(row, 2, u'__________ / %s/'%currentOrgMainStuff[0], self.getFormatGeneral(), CReportBase.AlignLeft)
        row = table.addRow()
        table.setText(row, 0, u'%d %s %dг.' %(date.day(), monthNameGC[date.month()], date.year()), self.getFormatGeneral(), CReportBase.AlignLeft)
        table.setText(row, 2, u'%d %s %dг.' %(date.day(), monthNameGC[date.month()], date.year()), self.getFormatGeneral(), CReportBase.AlignLeft)
        row = table.addRow()
        #table.setText(row, 0,u'                                                                                         '\
        #                     u'                                                                                         '\
        #                     u'
        #                                                                                          ', self.getFormatGeneral())
        self.docText = doc

    def getFormatGeneral(self):
        format = QtGui.QTextCharFormat()
        font = QtGui.QFont()
        font.setFamily('Times')
        font.setPointSize(10)
        format.setFont(font)
        return format

    def getFormatTitle(self):
        format = self.getFormatGeneral()
        font = format.font()
        font.setBold(True)
        format.setFont(font)
        return format

    def getBorderBrush(self):
        brush = QtGui.QBrush()
        brush.setColor(QtCore.Qt.black)
        brush.setStyle(QtCore.Qt.SolidPattern)
        return brush

    def getPrikFieldsWithDesc(self):
        return [
            ('ID',      'N', 7, 0,  u'Идентификатор', u'Уникальное числовое значение записи в пределах кода медицинской организации, используется для обратной связи'),
            ('IDSTR',   'N', 10, 0, u'Идентификатор', u'Для идентификации записей и установления однозначного соответствия между сведениями в краевом регистре и сведениями в информационных системах медицинской организаций'),
            ('SMO',     'C', 4,     u'Код СМО, в системе ОМС', u'Код СМО плательщика (SPR02, согласно Положения), для инокраевых - 9007'),
            ('DPFS',    'C', 1,     u'Тип документа, подтверждающего факт страхования -далее ДПФС', u'П-бумажный полис единого образца\nЭ-электронный полис единого образца\nВ-временное свидетельство\nС-полис старого образца'),
            ('DPFS_N',  'C', 20,    u'Номер ДПФС', u'Номер документа ДПФС. Для электронного полиса и бумажного полиса единого образца указывается Единый номер полиса, формата ХХХХХХХХХХХХХХХХ, где X - число от 0 до 9. Для временного свидетельства ХХХХХХХХХ, где X - число от 0 до 9. Для полиса старого образца указывается номер полиса'),
            ('FAM',     'C', 40,    u'Фамилия', u''),
            ('IM',      'C', 40,    u'Имя', u''),
            ('SEX',     'C',  1,    u'Пол', u'М/Ж'),
            ('DATR',    'D'    ,    u'Дата рождения', u''),
            ('SNILS',   'C', 14,    u'СНИЛС в формате ХХХ-ХХХ-ХХХ ХХ', u'Не заполняется в случае отсутствия сведений'),
            ('DOC',     'C',  2,    u'Тип документа УДЛ', u'SPR43, согласно Положения'),
            ('DOC_S',   'C', 10,    u'Серия документа УДЛ', u'Не обязательное поле. SPR43, согласно Положения Заполняется при наличии серии у документа'),
            ('DOC_N',   'C', 15,    u'Номер документа УДЛ', u'SPR43, согласно Положения'),
            ('CODE_MO', 'C', 5,     u'Код медицинской организации', u'Код медицинской организации (структурного подразделения, оказывающего амбулаторно-поликлиническую помощь), к которому прикреплен гражданин (SPR01, согласно Положения).'),
            ('OID_MO',  'C', 30,    u'Код медицинской организации из Паспорта ЛПУ', u'Реестр медицинских организаций, который ведёт Министерство здравоохранения в ИС «Паспорт ЛПУ»'),
            ('PRIK',    'C', 1,     u'Способ прикрепления', u'0-нет данных о способе прикрепления\n1-по месту регистрации\n2-по личному заявлению'),
            ('PRIK_D',  'D',        u'Дата прикрепления', u''),
            ('OTKR_D',  'D',        u'Дата открепления', u'Заполняется при откреплении пациента'),
            ('UCH',     'C', 5,     u'Номер участка', u''),
            ('R_NAME',  'C', 30,    u'Наименование района по месту регистрации пациента', u''),
            ('C_NAME',  'C', 30,    u'Наименование города', u'Не обязательное поле'),
            ('NP_NAME', 'C', 40,    u'Наименование населенного пункта по месту регистрации', u'Не обязательное поле'),
            ('UL_NAME', 'C', 40,    u'Наименование улицы', u''),
            ('DOM',     'C', 7,     u'Номер дома', u'')
            ]


    def getLgotaFieldsWithDesc(self):
        return [
            ('ID',         'N', 7, 0, u'Идентификатор', u'Уникальное числовое значение записи в пределах кода медицинской организации, используется для обратной связи и связи с файлом PRIKXXXXX'),
            ('CODE_MO',    'C', 5,    u'Код медицинской организации', u'Код медицинской организации (структурного подразделения, оказывающего амбулаторно-поликлиническую помощь), к которому прикреплен гражданин (SPR01, согласно Положения)'),
            ('LGOTA',      'C', 3,    u'Код льготы', u'Указывается код льготы на основании Приказа МЗ КК от 24.06.2013 № 2702'),
            ('DOCU',       'C', 150,  u'Наименование документа, подтверждающего право на льготу', u''),
            ('DOCU_N',     'C', 30,   u'Номер документа, подтверждающего право на льготу', u''),
            ('POLU_D',     'D',       u'Дата получения права на льготу', u'Дата получения права на льготу по категории'),
            ('ORON_D',     'D',       u'Дата окончания права на льготу', u'Не обязательное поле\nДата окончания права на льготу по категории (может быть пустой)'),
        ]

    def getUchFieldsWithDesc(self):
        return [
            ('CODE_MO',    'C',  5, u'Код медицинской организации', u'Код медицинской организации (структурного подразделения, оказывающего амбулаторно-поликлиническую помощь), к которому прикреплен гражданин (SPR01, согласно Положения)'),
            ('UCH',        'C',  5, u'Номер участка', u''),
            ('D_SPEC',     'C',  2, u'Категория медицинского работника', u'1 - врач\n2 - средний медицинский персонал'),
            ('D_FAM',      'C', 40, u'Фамилия врача', u''),
            ('D_IM',       'C', 40, u'Имя врача', u''),
            ('D_OT',       'C', 40, u'Отчество врача', u''),
            ('D_SNILS',    'C', 14, u'СНИЛС в формате ХХХ-ХХХ-ХХХ XX', u''),
            ('D_PRIK_UCH', 'D',     u'Дата прикрепления врача к участку', u''),
            ('D_OTKR_UCH', 'D',     u'Дата открепления (или увольнения) врача с участка', u''),
        ]