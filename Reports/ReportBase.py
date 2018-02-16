# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from ReportView import CReportViewDialog
from library.LoggingModule import Logger
from library.Utils import forceString, toVariant, getPref, getPrefBool, getPrefDate, getPrefInt, getPrefRef, \
    getPrefString, getPrefTime, setPref, firstYearDay


# обнаружено, что в некоторых случаях (напр., при запуске программы в kubuntu 8.04 и kubuntu 8.10)
# код
#   class CReportBase(object):
#       AlignLeft = QtGui.QTextBlockFormat()
#       AlignLeft.setAlignment(Qt.AlignLeft)
# приводит к дефектам изображения (неверно рисуется меню, для labels выделяется недостаточное пространство и пр.)
# вероятно, дело в кешировании оконной системой объектов соответствующих QtGui.QTextBlockFormat
# поэтому принято решение сделать их некешируемыми

class _CReportBaseMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(_CReportBaseMetaclass, cls).__init__(name, bases, dct)

    @property
    def AlignLeft(self):
        result = QtGui.QTextBlockFormat()
        result.setAlignment(QtCore.Qt.AlignLeft)
        return result

    @property
    def AlignCenter(self):
        result = QtGui.QTextBlockFormat()
        result.setAlignment(QtCore.Qt.AlignCenter)
        return result

    @property
    def AlignRight(self):
        result = QtGui.QTextBlockFormat()
        result.setAlignment(QtCore.Qt.AlignRight)
        return result

    @property
    def ReportTitle(self):
        result = QtGui.QTextCharFormat()
        result.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(2))
        result.setFontWeight(QtGui.QFont.Bold)
        return result

    @property
    def ReportSubTitle(self):
        result = QtGui.QTextCharFormat()
        result.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(1))
        result.setFontWeight(QtGui.QFont.Bold)
        return result

    @property
    def ReportBody(self):
        result = QtGui.QTextCharFormat()
        result.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(0))
        return result

    @property
    def TableBody(self):
        result = QtGui.QTextCharFormat()
        return result

    @property
    def TableHeader(self):
        result = QtGui.QTextCharFormat()
        result.setFontWeight(QtGui.QFont.Bold)
        result.setFontPointSize(10)
        return result

    @property
    def TableTotal(self):
        result = QtGui.QTextCharFormat()
        result.setFontWeight(QtGui.QFont.Bold)
        return result

    @property
    def TableAlignTop(self):
        result = QtGui.QTextTableFormat()
        result.setAlignment(QtCore.Qt.AlignTop)
        return result


class CReportBase(object):
    __metaclass__ = _CReportBaseMetaclass

    def __init__(self, parent=None):
        Logger.logWindowAccess(windowName=type(self).__name__, notes=u'Отчёт')

        self.__parent = parent
        self._title = ''
        self._preferences = ''
        self.viewerGeometry = None
        self.orientation = QtGui.QPrinter.Portrait
        self._queryText = u''

    def exec_(self):
        QtGui.qApp.call(self.__parent, self.reportLoop)

    def setOrientation(self, orientation):
        self.orientation = orientation

    def setQueryText(self, queryText):
        self._queryText = queryText

    def queryText(self):
        return self._queryText

    def addQueryText(self, queryText, queryDesc=u''):
        self._queryText += (queryDesc + u'\n' + queryText + u'\n\n')

    def getSetupDialog(self, parent):
        return None

    def reportLoop(self):
        params = self.getDefaultParams()
        while True:
            setupDialog = self.getSetupDialog(self.__parent)
            if setupDialog is not None:
                setupDialog.setParams(params)
                if not setupDialog.exec_():
                    break
                params = setupDialog.params()
            else:
                params = {}
            self.saveDefaultParams(params)
            reportResult = None
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                reportResult = self.build(params)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            if reportResult is None:
                break
            viewDialog = CReportViewDialog(self.__parent)
            if self.viewerGeometry:
                viewDialog.restoreGeometry(self.viewerGeometry)
            viewDialog.setWindowTitle(self.title())
            viewDialog.setRepeatButtonVisible()
            viewDialog.setText(reportResult)
            viewDialog.setOrientation(params.get('pageOrientation', self.orientation))
            viewDialog.setQueryText(self.queryText())
            pageFormat = self.getPageFormat()
            if pageFormat:
                viewDialog.setPageFormat(pageFormat)
            done = not viewDialog.exec_()
            self.viewerGeometry = viewDialog.saveGeometry()
            if done:
                break
                # save params?

    def oneShot(self, params):
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            reportResult = self.build(params)
        finally:
            QtGui.qApp.restoreOverrideCursor()
        viewDialog = CReportViewDialog(self.__parent)
        if self.viewerGeometry:
            viewDialog.restoreGeometry(self.viewerGeometry)
        viewDialog.setWindowTitle(self.title())
        viewDialog.setText(reportResult)
        viewDialog.exec_()
        self.viewerGeometry = viewDialog.saveGeometry()

    def setTitle(self, title, preferences=''):
        self._title = title
        if preferences:
            self._preferences = preferences
        else:
            self._preferences = title
        self.setVal(self.getDefaultParams())

    def title(self):
        return self._title

    def setVal(self, params):
        pass

    def patientRequired(self):
        return False

    def getDefaultParams(self):
        result = {}
        prefs = getPref(QtGui.qApp.preferences.reportPrefs, self._preferences, {})
        today = QtCore.QDate.currentDate()
        begYear = firstYearDay(today.addDays(-7))

        result['begDate'] = getPrefDate(prefs, 'begDate', begYear)
        result['begDateTalonSignal'] = getPrefDate(prefs, 'begDateTalonSignal', today.addDays(-1))
        result['endDate'] = getPrefDate(prefs, 'endDate', today.addDays(-1))
        result['begDateBeforeRecord'] = getPrefDate(prefs, 'begDateBeforeRecord',
                                                    QtCore.QDate(today.year(), today.month(), 1))
        result['endDateBeforeRecord'] = getPrefDate(prefs, 'endDateBeforeRecord', today.addDays(-1))
        result['Year'] = getPrefString(prefs, 'Year', '')
        result['begTime'] = getPrefTime(prefs, 'begTime', QtCore.QTime(0, 0))
        result['endTime'] = getPrefTime(prefs, 'endTime', QtCore.QTime(23, 59, 59))
        result['orgStructureId'] = getPrefRef(prefs, 'orgStructureId', None)
        result['personId'] = getPrefRef(prefs, 'personId', None)
        result['userProfileId'] = getPrefRef(prefs, 'userProfileId', None)
        result['beforeRecordUserId'] = getPrefRef(prefs, 'beforeRecordUserId', None)
        result['orgInsurerId'] = getPrefRef(prefs, 'orgInsurerId', None)
        result['profilBedId'] = getPrefRef(prefs, 'profilBedId', None)
        result['emergencyOrder'] = getPrefInt(prefs, 'emergencyOrder', 0)
        # для нетрудоспособности:
        result['byPeriod'] = getPrefBool(prefs, 'byPeriod', None)  # отбор по периоду
        result['doctype'] = getPrefRef(prefs, 'doctype', None)  # тип документа (листок, справка)
        result['tempInvalidReason'] = getPrefRef(prefs, 'tempInvalidReason',
                                                 None)  # причина временной нетрудоспособности
        result['durationFrom'] = getPrefInt(prefs, 'durationFrom', 0)  # фильтр по длительности
        result['durationTo'] = getPrefInt(prefs, 'durationTo', 0)  # фильтр по длительности
        result['sex'] = getPrefInt(prefs, 'sex', 0)
        result['ageFrom'] = getPrefInt(prefs, 'ageFrom', 0)
        result['ageTo'] = getPrefInt(prefs, 'ageTo', 150)
        result['socStatusClassId'] = getPrefRef(prefs, 'socStatusClassId', None)
        result['socStatusTypeId'] = getPrefRef(prefs, 'socStatusTypeId', None)
        result['onlyClosed'] = getPrefBool(prefs, 'onlyClosed', None)  # только закрытые
        #
        result['MKBFilter'] = getPrefInt(prefs, 'MKBFilter', 0)  # 0-нет фильтра, 1-интервал, 2-нет кода
        result['MKBFrom'] = getPrefString(prefs, 'MKBFrom', 'A00')
        result['MKBTo'] = getPrefString(prefs, 'MKBTo', 'Z99.9')
        result['MKBExFilter'] = getPrefInt(prefs, 'MKBExFilter', 0)  # 0-нет фильтра, 1-интервал, 2-нет кода
        result['MKBExFrom'] = getPrefString(prefs, 'MKBExFrom', 'A00')
        result['MKBExTo'] = getPrefString(prefs, 'MKBExTo', 'Z99.9')

        result['eventTypeId'] = getPrefRef(prefs, 'eventTypeId', None)
        result['actionTypeClass'] = getPrefInt(prefs, 'actionTypeClass', 0)
        result['actionTypeId'] = getPrefRef(prefs, 'actionTypeId', None)
        result['queueType'] = getPrefRef(prefs, 'queueType', None)
        result['onlyPermanentAttach'] = getPrefBool(prefs, 'onlyPermanentAttach', False)
        result['onlyPayedEvents'] = getPrefBool(prefs, 'onlyPayedEvents', False)
        result['begPayDate'] = getPrefDate(prefs, 'begPayDate', begYear)
        result['endPayDate'] = getPrefDate(prefs, 'endPayDate', QtCore.QDate())
        result['insurerId'] = getPrefRef(prefs, 'insurerId', None)
        result['contractPath'] = getPrefString(prefs, 'contractPath', '')
        #
        result['typeFinanceId'] = getPrefRef(prefs, 'typeFinanceId', None)
        result['tariff'] = getPrefInt(prefs, 'tariff', 0)
        result['visitPayStatus'] = getPrefInt(prefs, 'visitPayStatus', 0)
        result['groupingRows'] = getPrefInt(prefs, 'groupingRows', 0)
        result['rowGrouping'] = getPrefInt(prefs, 'rowGrouping', 0)
        #
        result['areaId'] = getPrefRef(prefs, 'areaId', None)
        result['characterClass'] = getPrefInt(prefs, 'characterClass', 0)

        result['onlyFirstTime'] = getPrefBool(prefs, 'onlyFirstTime', None)  # только первичные
        result['registeredInPeriod'] = getPrefBool(prefs, 'registeredInPeriod',
                                                   None)  # только зарегистрированные в период
        result['notNullTraumaType'] = getPrefBool(prefs, 'notNullTraumaType', None)  # только с указанием типа травмы
        result['accountAccomp'] = getPrefBool(prefs, 'accountAccomp', None)  # учитывать сопутствующие

        result['busyness'] = getPrefInt(prefs, 'business',
                                        0)  # учитывать занятость, 0-не учитывать, 1-только занятые, 2-только не занятые

        result['deathPlace'] = getPrefString(prefs, 'deathPlace', '')
        result['deathCause'] = getPrefString(prefs, 'deathCause', '')
        result['deathFoundBy'] = getPrefString(prefs, 'deathFoundBy', '')
        result['deathFoundation'] = getPrefString(prefs, 'deathFoundation', '')

        result['outputColumns'] = getPref(prefs, 'outputColumns', {})

        result['chkClientId'] = getPrefBool(prefs, 'chkClientId', False)
        result['chkEventId'] = getPrefBool(prefs, 'chkEventId', False)
        result['chkExternalEventId'] = getPrefBool(prefs, 'chkExternalEventId', False)

        result['chkRegAddress'] = getPrefBool(prefs, 'chkRegAddress', True)
        result['chkLocAddress'] = getPrefBool(prefs, 'chkLocAddress', True)
        result['chkContacts'] = getPrefBool(prefs, 'chkContacts', True)
        result['chkRelations'] = getPrefBool(prefs, 'chkRelations', True)
        result['chkDocument'] = getPrefBool(prefs, 'chkDocument', True)
        result['chkCompulsoryPolicy'] = getPrefBool(prefs, 'chkCompulsoryPolicy', True)
        result['chkVoluntaryPolicy'] = getPrefBool(prefs, 'chkVoluntaryPolicy', True)
        result['chkRelegateOrg'] = getPrefBool(prefs, 'chkRelegateOrg', True)
        result['deliveredOrg'] = getPrefBool(prefs, 'deliveredOrg', True)
        result['chkDeliveredOrg'] = getPrefBool(prefs, 'chkDeliveredOrg', True)
        result['chkRelegateOrgDiagnosis'] = getPrefBool(prefs, 'chkRelegateOrgDiagnosis', True)
        result['chkReceivedOrgDiagnosis'] = getPrefBool(prefs, 'chkReceivedOrgDiagnosis', True)
        result['chkLeavedInfo'] = getPrefBool(prefs, 'chkLeavedInfo', True)
        result['chkMessageToRelatives'] = getPrefBool(prefs, 'chkMessageToRelatives', True)
        result['chkNotes'] = getPrefBool(prefs, 'chkNotes', True)
        result['cmbOrderBy'] = getPrefBool(prefs, 'cmbOrderBy', True)
        result['chkSex'] = getPrefBool(prefs, 'chkSex', True)
        result['chkAge'] = getPrefBool(prefs, 'chkAge', True)
        result['chkHour'] = getPrefBool(prefs, 'chkHour', True)
        result['chkCardNumber'] = getPrefBool(prefs, 'chkCardNumber', True)
        result['chkNotHospitalized'] = getPrefBool(prefs, 'chkNotHospitalized', True)
        result['chkEventOrder'] = getPrefBool(prefs, 'chkEventOrder', True)
        result['chkBedProfile'] = getPrefBool(prefs, 'chkBedProfile', True)
        result['chkHospitalBedProfile'] = getPrefBool(prefs, 'chkHospitalBedProfile', False)
        result['chkOtherRelegateOrg'] = getPrefBool(prefs, 'chkOtherRelegateOrg', True)

        geometry = getPref(prefs, 'viewerGeometry', None)
        if type(geometry) == QtCore.QVariant and geometry.type() == QtCore.QVariant.ByteArray and not geometry.isNull():
            self.viewerGeometry = geometry.toByteArray()
        return result

    def saveDefaultParams(self, params):
        prefs = {}
        # FIXME: atronah: мне жутко.. Зачем сохранять все params, если обратно потом грузятся только некоторые, указанные явно в getDefaultParams
        for param, value in params.iteritems():
            setPref(prefs, param, toVariant(value))
        if self.viewerGeometry:
            setPref(prefs, 'viewerGeometry', toVariant(self.viewerGeometry))
        setPref(QtGui.qApp.preferences.reportPrefs, self._preferences, prefs)

    def build(self, params):
        return ''

    def getPageFormat(self):
        return None


##Вставляет поле для подписей (таблицу с невидимыми границами)
# Поле для подписей, в котором каждой должности из titles
# соответствует строка с названием должности, местом для подписи и именем из names, вида:
#
#     <Должность_из_titles>    _____________________        <Ф.И.О_из_names>
#                                     (подпись)          (расшифровка подписи)
#
# @param cursor ссылка на объект типа QTextCursor - место документа, куда будет вставляться поле подписей
# @param titles список лиц, которые должны поставить подписи (должности)
# @param names список имен (Ф.И.О), соответствующих перечисленным в titles должностям (если None, то вставляется "_________________")
# @param charFormat ссылка на объект QTextCharFormat для указания оформления поля
# @param sealOverTitle индекс должности из titles НАД указанием которого будет ставится знак М.П. (Место печати)
# @param colCount количество столбцов в поле подписей, где каждый столбец включает в себя 3 подстолбца (длжность, подпись, расшифровка)
# @param signLabel текстовый комментарий под полем подписи
# @param transcriptLabel текстовый комментарий под полем имени (расшифровка подписи)
# @param isAddSignatureField указывает на необходимость добавлять поле для подписи (True по умолчанию)
# FIXME: Atronah: list(titles) & list(names) -> dict(titles, names)
def createAutographField(cursor, titles, names, charFormat=QtGui.QTextCharFormat(), sealOverTitle=None, colCount=1,
                         signLabel=u'(подпись)', transcriptLabel='', isAddSignatureField=True):
    if titles:
        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setBorder(0)
        tableFormat.setBorderStyle(QtGui.QTextFrameFormat.BorderStyle_None)
        tableFormat.setAlignment(QtCore.Qt.AlignLeft)
        tableFormat.setCellSpacing(5)
        if not isinstance(titles, list):
            list(titles)
        blockFormat = QtGui.QTextBlockFormat()
        titlesCount = len(titles)
        subRowCount = 2 if sealOverTitle is None else 3
        leftEmptyColumns = 1
        rowCount = int(0.5 + float(titlesCount) / colCount) * subRowCount
        subColumnCount = 4 if isAddSignatureField else 3
        table = cursor.insertTable(rowCount, leftEmptyColumns + colCount * subColumnCount, tableFormat)
        itemNumber = 0
        row = 0
        column = 0
        for title in titles:
            columnOffset = 0
            sealRow = 0
            if sealOverTitle == itemNumber:
                cellCursor = table.cellAt(row * subRowCount + 0 + sealRow,
                                          leftEmptyColumns + column * 4).firstCursorPosition()
                blockFormat.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                cellCursor.setBlockFormat(blockFormat)
                cellCursor.insertText(u'М.П.', charFormat)
                sealRow = 1

            name = names[itemNumber] if names[itemNumber] else u'    __________________________    '
            # запись названия должности
            cellCursor = table.cellAt(row * subRowCount + 0 + sealRow,
                                      leftEmptyColumns + column * subColumnCount + columnOffset).firstCursorPosition()
            blockFormat.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
            cellCursor.setBlockFormat(blockFormat)
            cellCursor.insertText(unicode(title), charFormat)
            columnOffset += 1
            # вставка поля для подписи
            if isAddSignatureField:
                cellCursor = table.cellAt(row * subRowCount + 0 + sealRow,
                                          leftEmptyColumns + column * subColumnCount + 1).firstCursorPosition()
                blockFormat.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
                cellCursor.setBlockFormat(blockFormat)
                cellCursor.insertText(u'    __________________________    ', charFormat)
                # вставка комментария к полю для подписи
                cellCursor = table.cellAt(row * subRowCount + 1 + sealRow,
                                          leftEmptyColumns + column * subColumnCount + 1).firstCursorPosition()
                blockFormat.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
                cellCursor.setBlockFormat(blockFormat)
                cellCursor.insertText(signLabel, charFormat)
                columnOffset += 1
            # вставка расшифровки подписи (имени сотрудника)
            cellCursor = table.cellAt(row * subRowCount + 0 + sealRow,
                                      leftEmptyColumns + column * subColumnCount + columnOffset).firstCursorPosition()
            blockFormat.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
            cellCursor.setBlockFormat(blockFormat)
            cellCursor.insertText(name, charFormat)
            # вставка комментария к полю для расшифровки подписи
            cellCursor = table.cellAt(row * subRowCount + 1 + sealRow,
                                      leftEmptyColumns + column * subColumnCount + columnOffset).firstCursorPosition()
            blockFormat.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            cellCursor.setBlockFormat(blockFormat)
            cellCursor.insertText(transcriptLabel, charFormat)
            columnOffset += 1
            # вставка пустого поля
            cellCursor = table.cellAt(row * subRowCount + 1 + sealRow,
                                      leftEmptyColumns + column * subColumnCount + columnOffset).firstCursorPosition()
            blockFormat.setAlignment(QtCore.Qt.AlignLeft)
            cellCursor.insertText(u'\t', charFormat)
            itemNumber += 1
            if column + 1 < colCount:
                column += 1
            else:
                column = 0
                row += 1


def insertRequisitesBlock(cursor, recipientId, payerId):
    def getOrgDetails(orgId):
        db = QtGui.qApp.db
        tableOrganisation = db.table('Organisation')
        tableOrgAccount = db.table('Organisation_Account')
        tableBank = db.table('Bank')
        table = tableOrganisation.leftJoin(tableOrgAccount,
                                           tableOrgAccount['organisation_id'].eq(tableOrganisation['id']))
        table = table.leftJoin(tableBank, tableBank['id'].eq(tableOrgAccount['bank_id']))
        cond = [tableOrganisation['id'].eq(orgId)]
        cols = [tableOrganisation['fullName'],
                tableOrganisation['Address'],
                tableOrganisation['INN'],
                tableOrganisation['KPP'],
                tableOrgAccount['name'].alias('accountName'),
                tableBank['name'].alias('bankName'),
                tableBank['BIK']]
        record = db.getRecordEx(table, cols, cond)
        if record:
            orgName = forceString(record.value('fullName'))
            orgAddress = forceString(record.value('address'))
            orgINN = forceString(record.value('INN'))
            orgKPP = forceString(record.value('KPP'))
            orgAccount = forceString(record.value('accountName'))
            bankName = forceString(record.value('bankName'))
            bankBIK = forceString(record.value('BIK'))
            return {'orgName': orgName,
                    'orgAddress': orgAddress,
                    'orgINN': orgINN,
                    'orgKPP': orgKPP,
                    'orgAccount': orgAccount,
                    'bankName': bankName,
                    'bankBIK': bankBIK}
        else:
            return {'orgName': '',
                    'orgAddress': '',
                    'orgINN': '',
                    'orgKPP': '',
                    'orgAccount': '',
                    'bankName': '',
                    'bankBIK': ''}

    recipient = getOrgDetails(recipientId)
    payer = getOrgDetails(payerId)

    tableFormat = QtGui.QTextTableFormat()
    tableFormat.setBorder(0)
    tableFormat.setBorderStyle(QtGui.QTextFrameFormat.BorderStyle_None)
    tableFormat.setAlignment(QtCore.Qt.AlignLeft)

    # tableFormat.setRightMargin(60)
    # if not isinstance(titles, list):
    #    list(titles)
    # blockFormat = QtGui.QTextBlockFormat()
    # titlesCount = len(titles)
    # subRowCount = 2 if sealOverTitle is None else 3
    # leftEmptyColumns = 1
    # rowCount = int(0.5 + float(titlesCount) / colCount) * subRowCount
    # subColumnCount = 4 if isAddSignatureField else 3
    table = cursor.insertTable(3, 4, tableFormat)

    font = QtGui.QFont()
    font.setBold(True)
    titleFormat = QtGui.QTextCharFormat()
    titleFormat.setFont(font)

    table.cellAt(0, 0).firstCursorPosition().insertText(u'Поставщик', titleFormat)
    table.cellAt(0, 2).firstCursorPosition().insertText(u'Плательщик', titleFormat)
    table.cellAt(1, 0).firstCursorPosition().insertText(u'Расчетный счёт', titleFormat)
    table.cellAt(1, 2).firstCursorPosition().insertText(u'Расчетный счёт', titleFormat)
    table.cellAt(2, 0).firstCursorPosition().insertText(u'Адрес', titleFormat)
    table.cellAt(2, 2).firstCursorPosition().insertText(u'Адрес', titleFormat)
    table.cellAt(0, 1).firstCursorPosition().insertText(recipient['orgName'] + u'\t\t')
    table.cellAt(0, 3).firstCursorPosition().insertText(payer['orgName'])
    table.cellAt(1, 1).firstCursorPosition().insertText(u'ИНН: %s КПП: %s\n%s\nр/с %s БИК %s' %
                                                        (recipient['orgINN'], recipient['orgKPP'],
                                                         recipient['bankName'], recipient['orgAccount'],
                                                         recipient['bankBIK']))
    table.cellAt(1, 3).firstCursorPosition().insertText(u'ИНН: %s КПП: %s\n%s\nр/с %s БИК %s' %
                                                        (payer['orgINN'], payer['orgKPP'],
                                                         payer['bankName'], payer['orgAccount'],
                                                         payer['bankBIK']))
    table.cellAt(2, 1).firstCursorPosition().insertText(recipient['orgAddress'])
    table.cellAt(2, 3).firstCursorPosition().insertText(payer['orgAddress'])


def createTable(testCursor, columnDescrs, headerRowCount=1, border=1, cellPadding=2, cellSpacing=0,
                charFormat=CReportBase.TableHeader, borderBrush=None, repeatHeader=True):
    def widthToTextLenght(width):
        widthSpec = QtGui.QTextLength.VariableLength
        widthVal = 0
        try:
            if isinstance(width, basestring):
                if len(width) > 0:
                    if width[-1:] == '%':
                        widthVal = float(width[:-1])
                        widthSpec = QtGui.QTextLength.PercentageLength
                    elif width[-1:] == '?':
                        widthVal = float(width[:-1])
                        widthSpec = QtGui.QTextLength.VariableLength
                    elif width[-1:] == '=':
                        widthVal = float(width[:-1])
                        widthSpec = QtGui.QTextLength.FixedLength
                    else:
                        widthVal = float(width)
                        widthSpec = QtGui.QTextLength.FixedLength
            else:
                widthVal = float(width)
                widthSpec = QtGui.QTextLength.FixedLength
        except:
            pass
        return QtGui.QTextLength(widthSpec, widthVal)

    columnWidthConstraints = []
    columnNames = []
    #        headerRowCount = 1
    for columnDescr in columnDescrs:
        assert type(columnDescr) == tuple
        if len(columnDescr) == 4:
            name, width, headers, align = columnDescr
        else:
            width, headers, align = columnDescr
            name = None
        columnNames.append(name)
        columnWidthConstraints.append(widthToTextLenght(width))
        if type(headers) == list:
            headerRowCount = max(headerRowCount, len(headers))

    tableFormat = QtGui.QTextTableFormat()
    tableFormat.setBorder(border)
    tableFormat.setCellPadding(cellPadding)
    tableFormat.setCellSpacing(cellSpacing)
    tableFormat.setColumnWidthConstraints(columnWidthConstraints)
    if repeatHeader:
        tableFormat.setHeaderRowCount(headerRowCount)
    if borderBrush:
        tableFormat.setBorderBrush(borderBrush)
    table = testCursor.insertTable(max(1, headerRowCount), max(1, len(columnDescrs)), tableFormat)

    aligns = []
    for column, columnDescr in enumerate(columnDescrs):
        assert type(columnDescr) == tuple
        # получение параметров с учетом возможного наличия имени в первом элементе описания
        width, headers, align = columnDescr if len(columnDescr) != 4 else columnDescr[1:]
        if type(headers) != list:
            headers = [headers]

        for row, header in enumerate(headers):
            if header != CReportTableBase.ColumnIndex and header == '':
                continue
            cellCursor = table.cellAt(row, column).firstCursorPosition()
            cellCursor.setBlockFormat(CReportBase.AlignCenter)
            # ---hided by atronah 28.05.2012 for 344#cellCursor.setCharFormat(CReportBase.TableHeader)
            cellCursor.setCharFormat(charFormat)
            cellCursor.insertText(forceString(column + 1) if header == CReportTableBase.ColumnIndex else header)

        aligns.append(align)

    return CReportTableBase(table, aligns, columnNames)


class CReportTableBase(object):
    ColumnIndex = object()

    def __init__(self, table, aligns, columnNames=[]):
        self.table = table  # type: QtGui.QTextTable
        self.aligns = aligns
        for columnIdx, columnName in enumerate(columnNames):
            if columnName is None or hasattr(self, columnName):
                continue
            setattr(self, columnName, columnIdx)

    def mergeCells(self, row, column, numRows, numCols):
        self.table.mergeCells(row, column, numRows, numCols)

    def addRow(self):
        row = self.table.rows()
        self.table.insertRows(row, 1)
        return row

    def addCol(self):
        col = self.table.columns()
        self.table.insertColumns(col, 1)
        return col

    def addRowWithContent(self, *args, **kwargs):
        row = self.addRow()
        for i, txt in enumerate(args):
            self.setText(row, i, txt, kwargs.get('charFormat', None))
        return row

    def addRowWithHtmlContent(self, *args):
        row = self.addRow()
        for i, txt in enumerate(args):
            self.setHtml(row, i, txt)
        return row

    def addRows(self, rows, charFormat=None, blockFormat=None, isHtml=False):
        rowIdx = self.table.rows()
        for i, row in enumerate(rows):
            self.table.appendRows(1)
            for j, text in enumerate(map(unicode, row)):
                cursor = self.table.cellAt(rowIdx + i, j).lastCursorPosition()
                if isHtml:
                    cursor.insertHtml(text)
                else:
                    cursor.insertText(text)
        return rowIdx

    def rows(self):
        return self.table.rows()

    def cols(self):
        return self.table.cols()

    def cellAt(self, row, column):
        return self.table.cellAt(row, column)

    def cursorAt(self, row, column):
        return self.cellAt(row, column).lastCursorPosition()

    # def clearCell(self, row, column):
    #     cursor = self.cursorAt(row, column)
    #     cursor.select(cursor.BlockUnderCursor)
    #     cursor.removeSelectedText()

    def clearCell(self, row, col):
        cursor = self.cursorAt(row, col)
        maxIterations = 100
        while (cursor.position() - cursor.block().position()) > 0 and maxIterations > 0:
            maxIterations -= 1
            cursor.deletePreviousChar()

    def setText(self, row, column, text, charFormat=None, blockFormat=None, brushColor=None, fontBold=None,
                clearBefore=False):
        if clearBefore:
            self.clearCell(row, column)
        cursor = self.cursorAt(row, column)
        tableFormat = None
        if brushColor:
            tableFormat = QtGui.QTextCharFormat()
            tableFormat.setBackground(QtGui.QBrush(brushColor))
            cursor.setBlockCharFormat(tableFormat)
        if fontBold:
            font = QtGui.QFont()
            font.setBold(True)
            tableFormat = QtGui.QTextCharFormat()
            tableFormat.setFont(font)
        if blockFormat:
            cursor.setBlockFormat(blockFormat)
        elif column in self.aligns:
            cursor.setBlockFormat(self.aligns[column])
        if charFormat:
            cursor.setCharFormat(charFormat)
        elif tableFormat:
            cursor.setCharFormat(tableFormat)
        cursor.deletePreviousChar()
        cursor.insertText(unicode(text))

    def setTable(self, row, column, columnDescrs, headerRowCount=1, border=1, cellPadding=2, cellSpacing=0):
        cursor = self.cursorAt(row, column)
        return createTable(cursor, columnDescrs, headerRowCount, border, cellPadding, cellSpacing)

    def setHtml(self, row, column, html):
        cursor = self.cursorAt(row, column)
        #        cursor.setBlockFormat(self.aligns[column])
        #        if charFormat:
        #            cursor.setCharFormat(charFormat)
        cursor.insertHtml(html)
