# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import datetime
import os
import os.path
from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrganisationInfo
from Registry.MIACExchange.DDMonitoringSender import CMIACDDMonitoringSender
from Registry.MIACExchange.Preferences import CMIACExchangePreferences
from Reports.Report import normalizeMKB, CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog
from Reports.StatReport1NPUtil import havePermanentAttach
from Ui_ReportF12_D_3_MSave import Ui_ReportF12_D_3_MSaveDialog
from Ui_ReportF12_D_3_MSetup import Ui_ReportF12_D_3_MSetupDialog
from library import SendMailDialog
from library.CalcCheckSum import calcCheckSum
from library.DialogBase import CDialogBase
from library.MapCode import createMapCodeToRowIdx
from library.Utils import forceBool, forceDate, forceInt, forceString, toVariant, getVal, \
    getPrefInt
from library.database import addDateInRange
from library.subst import substFields

Rows = [
        (u'Туберкулез',                                               '1', 'A15-A19'),
        (u'Злокачественные новообразования:',                         '',  'C15-C97'),
        (u'органов пищеварения',                                      '2', 'C15-C26'),
        (u'трахеи, бронхов, легкого',                                 '3', 'C33-C34'),
        (u'кожи',                                                     '4', 'C43-C44'),
        (u'молочной железы',                                          '5', 'C50'),
        (u'женских половых органов',                                  '6', 'C50-C58'),
        (u'предстательной железы',                                    '7', 'C61'),
        (u'лимфатической и кроветворной ткани',                       '8', 'C81-C96'),
        (u'Анемия',                                                   '9', 'D50-D64'),
        (u'Сахарный диабет',                                          '10','E10-E14'),
        (u'Ожирение',                                                 '11','E66'),
        (u'Нарушения обмена липопротеидов',                           '12','E78'),
        (u'Болезни, характеризующиеся повышенным кровяным давлением', '13','I10-I15'),
        (u'Ишемические болезни сердца',                               '14','I20-I25'),
        (u'Повышенное содержание глюкозы в крови' ,                   '15','R73'),
        (u'Отклонения от нормы, выявленные при получении диагностического изображения в ходе исследования легких','16','R91'),
        (u'Отклонения от нормы, выявленные при получении диагностического изображения в ходе исследования молочной железы','17','R92'),
        (u'Отклонения от нормы, выявленные при проведении функциональных исследований сердечно-сосудистой системы','18','R94.3'),
       ]


def countByGroups(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt='''
        SELECT
            isEventPayed(Event.id) as `done`,
            rbHealthGroup.code as `group`,
            COUNT(Event.id) as cnt
        FROM
            Event
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN Diagnostic    ON (     Diagnostic.event_id = Event.id
                                         AND Diagnostic.diagnosisType_id = (SELECT id FROM rbDiagnosisType WHERE code = '1')
                                       )
            LEFT JOIN rbHealthGroup ON rbHealthGroup.id = Diagnostic.healthGroup_id
            LEFT JOIN Account_Item  ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                       )
        WHERE
            %s
        GROUP BY
            `done`, `group`
    '''
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    return db.query(stmt % (db.joinAnd(cond)))


def selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt='''
        SELECT
            Event.client_id AS client_id,
            Diagnosis.mkb AS mkb
        FROM
            Diagnostic
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN Event     ON Event.id = Diagnostic.event_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbDiseaseStage     ON rbDiseaseStage.id     = Diagnostic.stage_id
            LEFT JOIN rbHealthGroup      ON rbHealthGroup.id      = Diagnostic.healthGroup_id
            LEFT JOIN rbDispanser        ON rbDispanser.id        = Diagnostic.dispanser_id
            LEFT JOIN Client             ON Client.id             = Event.client_id
            LEFT JOIN Account_Item  ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                       )
        WHERE
            rbDiseaseCharacter.code IN ('1', '2') AND
            %s
        GROUP BY
            Event.client_id, Diagnosis.mkb
    '''
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    return db.query(stmt % (db.joinAnd(cond)))


class CStatReportF12_D_3_M(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
#        self.setOwnershipVisible(True)
#        self.setWorkTypeVisible(True)
        self.setTitle(u'Сведения о дополнительной диспансеризации работающих граждан, Ф.№ 12-Д-3-M',
                      u'Сведения о дополнительной диспансеризации работающих граждан')


    def getSetupDialog(self, parent):
        result = CReportF12_D_3_MSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def getDefaultParams(self):
        result = CReport.getDefaultParams(self)
        prefs = dict()  # getPref(QtGui.qApp.preferences.reportPrefs, self._CReportBase__preferences, {})
        result['tbl1000Col3']     = getPrefInt(prefs, 'tbl1000Col3', 0)
        result['tbl1000Col4']     = getPrefInt(prefs, 'tbl1000Col4', 0)
        result['tbl1000Col5']     = getPrefInt(prefs, 'tbl1000Col5', 0)
        result['tbl1000Col6']     = getPrefInt(prefs, 'tbl1000Col6', 0)
        result['tbl1000Col7']     = getPrefInt(prefs, 'tbl1000Col7', 0)
        result['tbl1000Col8']     = getPrefInt(prefs, 'tbl1000Col8', 0)
        result['tbl2000Col3']     = getPrefInt(prefs, 'tbl2000Col3', 0)
        #result['NotComplete']     = getPrefInt(prefs, 'NotComplete', 0)
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        t1000 = self.build1000(cursor,  params)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        t2000 = self.build2000(cursor, begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, params)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        t3000 = self.build3000(cursor, begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        return doc, CExportDDMonitoringEIS(t2000, t3000),  CExportDDMonitoringXML(params, t2000, t3000)

    def build1000(self,  cursor, params):
        cursor.insertText(u'(1000)')
        cursor.insertBlock()
        tableColumns = [
            ('5%', [u'',
                     '',
                     '',
                     '1'], CReportBase.AlignLeft),
            ('5%',  [u'№ строки',
                     '',
                     '',
                     '2'], CReportBase.AlignCenter),
            ('10%',  [u'Всего',
                     '',
                     '',
                     '3'], CReportBase.AlignRight),
            ('10%',  [u'из них',
                     u'в полном объеме собственными силами',
                     '',
                     '4'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'на договорной основе в связи с отсутствием',
                     u' необходимого диагностического оборудования ',
                     '5'], CReportBase.AlignRight),
            ('10%',  [u'',
                     '',
                     u'необходимых специалистов',
                     '6'], CReportBase.AlignRight),
            ('10%',  ['',
                     '',
                     u'необходимых специалистов и диагностического оборудования ',
                     '7'], CReportBase.AlignRight),
            ('10%',  [u'Число организаций, прикрепленных к учреждениям здравоохранения для прохождения дополнительной диспансеризации ',
                     '',
                     u'',
                     '8'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 3)
        table.mergeCells(0, 7, 3, 1)
        i = table.addRow()

        table.setText(i, 0, u'Всего')
        table.setText(i, 1, '01')
        table.setText(i, 2, forceString(params.get('tbl1000Col3', u'-')))
        table.setText(i, 3, forceString(params.get('tbl1000Col4', u'-')))
        table.setText(i, 4, forceString(params.get('tbl1000Col5', u'-')))
        table.setText(i, 5, forceString(params.get('tbl1000Col6', u'-')))
        table.setText(i, 6, forceString(params.get('tbl1000Col7', u'-')))
        table.setText(i, 7, forceString(params.get('tbl1000Col8', u'-')))
        return {}


    def build2000(self, cursor, begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, params):
        query = countByGroups(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        totalDone = 0
        totalContinued = 0
        totalByGroup = [0]*5
        while query.next() :
            record = query.record()
            done = forceBool(record.value('done'))
            group = forceInt(record.value('group'))
            cnt = forceInt(record.value('cnt'))
            if done:
                totalDone += cnt
                if 0<group<=5:
                    totalByGroup[group-1] += cnt
            else:
                totalContinued += cnt

        # now text
        cursor.insertText(u'(2000)')
        cursor.insertBlock()
        tableColumns = [
            ('5%', [u'',
                     '',
                     '1'], CReportBase.AlignLeft),
            ('5%',  [u'№ строки',
                     '',
                     '2'], CReportBase.AlignCenter),
            ('10%',  [u'Число граждан',
                     u'подлежащих дополнительной диспансеризации',
                     '3'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'прошедших дополнительную диспансеризацию за отчетный период (законченный случай)',
                     '4'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'проходящих дополнительную диспансеризацию в отчетном периоде (незаконченный случай)',
                     '5'], CReportBase.AlignRight),
            ('10%',  [u'Распределение граждан, прошедших дополнительную диспансеризацию, по группам состояния здоровья',
                     u'I группа - практически здоровые',
                     '6'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'II группа - риск развития заболеваний',
                     '7'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'III группа - нуждаются в дополнительном обследовании, лечении в амбулаторно- поликлинических условиях',
                     '8'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'IV группа - нуждаются в дополнительном обследовании, лечении в стационарах',
                     '9'], CReportBase.AlignRight),
            ('10%',  ['',
                     u'V группа - нуждаются в высокотехнологичной медицинской помощи (ВМП)',
                     '10'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 5)
        i = table.addRow()

        table.setText(i, 0, u'Всего')
        table.setText(i, 1, '01')
        table.setText(i, 2, forceString(params.get('tbl2000Col3', u'-')))
        table.setText(i, 3, totalDone)
        table.setText(i, 4, totalContinued)
        for j in xrange(len(totalByGroup)):
            table.setText(i, 5+j, totalByGroup[j])
        return (totalDone, totalContinued, totalByGroup)


    def build3000(self, cursor, begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
        mapRows = createMapCodeToRowIdx( [row[2] for row in Rows] )
        reportRowSize = 1
        reportData = [ [0] * reportRowSize for row in Rows ]
        query = selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)

        while query.next():
            record = query.record()
            clientId = forceInt(record.value('client_id'))
            mkb      = normalizeMKB(forceString(record.value('mkb')))

            diagRows = mapRows.get(mkb, [])
            for row in diagRows:
                reportData[row][0] += 1

        # now text
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Результаты дополнительной диспансеризации работающих граждан')
        cursor.insertBlock()
        cursor.insertText(u'(3000)')
        cursor.insertBlock()

        tableColumns = [
            ('50%', [u'Заболевания и отклонения от нормы, выявленные при клинических и лабораторных исследованиях',  '1'], CReportBase.AlignLeft),
            ('5%',  [u'№ строки',      u'2'], CReportBase.AlignCenter),
            ('5%',  [u'Код по МКБ-10', u'3'], CReportBase.AlignCenter),
            ('30%', [u'Число заболеваний, впервые выявленных у граждан во время дополнительной диспансеризации', u'4'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)

        result = {}
        for iRow, row in enumerate(Rows):
            i = table.addRow()
            for j in xrange(3):
                table.setText(i, j, row[j])
            for j in xrange(reportRowSize):
                table.setText(i, 3+j, reportData[iRow][j])
            result[row[2]] = reportData[iRow][0]
        return result



class CExportDDMonitoringEIS(object):
    def __init__(self, t2000, t3000):
        self.t2000 = t2000
        self.t3000 = t3000
        self.name = u'Передать В МИАЦ'
        self.title = u'Передача В МИАЦ'
        self.MIACExchangePreferences = CMIACExchangePreferences()

    def getName(self):
        return self.name


    def isEnabled(self):
        return self.MIACExchangePreferences.isValid()


    def exec_(self, widget):
        try:
            tmpDir = QtGui.qApp.getTmpDir('eisoms')
            try:
                sender = CMIACDDMonitoringSender(tmpDir, self.MIACExchangePreferences.compress)
                sender.writeData(self.t2000, self.t3000)
                sender.close()
                sender.send(self.MIACExchangePreferences.address, self.MIACExchangePreferences.postBoxName)
            finally:
                QtGui.qApp.removeTmpDir(tmpDir)
            QtGui.QMessageBox.information( widget,
                                        self.title,
                                        u'Завершено успешно',
                                        QtGui.QMessageBox.Close)
        except:
            QtGui.QMessageBox.critical( widget,
                                        self.title,
                                        u'Ошибка передачи данных',
                                        QtGui.QMessageBox.Close)


class CExportDDMonitoringXML(object):
    def __init__(self, params, t2000, t3000):
        self.t2000 = t2000
        self.t3000 = t3000
        self.name = u'Экспорт в XML'
        self.title = u'Передача В МИАЦ в формате XML'
        self.params = params


    def getName(self):
        return self.name


    def isEnabled(self):
        return True


    def exec_(self, widget):
        try:
            dlg = CReportF12_D_3_MSaveDialog(widget,  self.params,  self.t2000, self.t3000)
            dlg.exec_()
        except:
            QtGui.QMessageBox.critical( widget,
                                        self.title,
                                        u'Ошибка передачи данных',
                                        QtGui.QMessageBox.Close)


class CReportF12_D_3_MSaveDialog(CDialogBase, Ui_ReportF12_D_3_MSaveDialog):
    def __init__(self, parent, params,  t2000, t3000):
        CDialogBase.__init__(self, parent)
        self.fileExt = '.xml'
        self.t2000 = t2000
        self.t3000 = t3000
        self.params = params
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.writtenFileName = ''


    def preSetupUi(self):
        pass


    def postSetupUi(self):
        miacCode = forceString(QtGui.qApp.db.translate('Organisation',
                'id', QtGui.qApp.currentOrgId(), 'miacCode'))

        month = forceString(self.params.get('endDate', QtCore.QDate()).month())
        self.fileName = u''+ month+u'_12d3m_'+miacCode
        self.nameEdit.setText(self.fileName)
        self.edtFileDir.setText(forceString(getVal(
            QtGui.qApp.preferences.appPrefs, 'ReportF12_D_3_MSaveFileDir', '')))
        self.checkName()

        if miacCode == '':
            QtGui.QMessageBox.warning(self,
                    u'Экспорт 12-Д-3-М в XML',
                    u'Отсутствует код МИАЦ для вашего ЛПУ.\n'
                    u'Необходимо установить код в:\n'
                    u'"Справочники.Организации.Организаци".',
                    QtGui.QMessageBox.Close)

            self.saveButton.setEnabled(False)
            self.btnSendMail.setEnabled(False)


    def checkName(self):
        self.saveButton.setEnabled(
            self.nameEdit.text()!='' and self.edtFileDir.text()!='')


    def createXML(self):
        try:
            miacCode = forceString(QtGui.qApp.db.translate('Organisation',
                'id', QtGui.qApp.currentOrgId(), 'miacCode'))

            if miacCode == '':
                QtGui.QMessageBox.warning(self,
                    u'Экспорт 12-Д-3-М в XML',
                    u'Отсутствует код МИАЦ для вашего ЛПУ.\n'
                    u'Необходимо установить код в:\n'
                    u'"Справочники.Организации.Организаци".',
                    QtGui.QMessageBox.Close)

                self.saveButton.setEnabled(False)
                self.btnSendMail.setEnabled(False)
                return

            dir = forceString(self.edtFileDir.text())
            fName = self.fileName+'.xml'
            self.writtenFileName = os.path.join(dir, fName)
            outFile = QtCore.QFile(self.writtenFileName)

            if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
                QtGui.QMessageBox.warning(self, u'Экспорт формы Ф-12-Д-3-М',
                                      u'Не могу открыть файл для записи %s:\n%s.'  %\
                                      (self.writtenFileName, outFile.errorString()))

            myXmlStreamWriter = CMyXmlStreamWriter(self)
            myXmlStreamWriter.writeFile(outFile,  self.params,  self.t2000,  self.t3000)
            outFile.close()

            self.btnSendMail.setEnabled(True)
            self.reportButton.setEnabled(True)
            QtGui.qApp.preferences.appPrefs['ReportF12_D_3_MSaveFileDir'] = \
                toVariant(self.edtFileDir.text())
            QtGui.QMessageBox.information(self, u'Экспорт в XML',
                u'Файл "%s" сохранен успешно.' % self.writtenFileName,
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        except Exception, e:
            QtGui.qApp.logCurrentException()
            self.btnSendMail.setEnabled(False)
            self.reportButton.setEnabled(False)
            self.writtenFileName = ''
            QtGui.QMessageBox.critical(self,
                                        u'Произошла ошибка',
                                        unicode(e),
                                        QtGui.QMessageBox.Close)



    @QtCore.pyqtSlot(QtCore.QString)
    def on_nameEdit_textChanged(self, string):
        self.fileName = forceString(self.nameEdit.text())
        self.checkName()


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileDir_textChanged(self, string):
        self.checkName()


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dirName = forceString(QtGui.QFileDialog.getExistingDirectory(
            self, u'Укажите каталог', self.edtFileDir.text()))
        if dirName != '':
            self.edtFileDir.setText(dirName)
            self.checkName()


    @QtCore.pyqtSlot()
    def on_btnSendMail_clicked(self):
        if self.writtenFileName:
            db = QtGui.qApp.db
            record = db.getRecordEx('rbAccountExportFormat', '*', 'prog=\'F12_D_3_M\'')
            if record:
                emailTo = forceString(record.value('emailTo'))
                subject = forceString(record.value('subject'))
                message = forceString(record.value('message'))
            else:
                emailTo = u'ddm.data@miac.zdrav.spb.ru'
                subject = u'Форма 12-Д-3-М'
                message = u'Уважаемые господа,\n'                       \
                          u'зацените результаты доп. диспансеризации\n' \
                          u'в {shortName}, ОГРН: {OGRN}\n'              \
                          u'за период с {begDate} по {endDate}\n'       \
                          u'\n'                                         \
                          u'--\n'                                       \
                          u'WBR\n'                                      \
                          u'{shortName}\n'

            orgRec=QtGui.qApp.db.getRecord(
                'Organisation', 'INN, OGRN, shortName', QtGui.qApp.currentOrgId())
            data = {}
            data['INN'] = forceString(orgRec.value('INN'))
            data['OGRN'] = forceString(orgRec.value('OGRN'))
            data['shortName'] = forceString(orgRec.value('shortName'))
            data['begDate'] = forceString(self.params.get('begDate', QtCore.QDate()))
            data['endDate'] = forceString(self.params.get('endDate', QtCore.QDate()))
            subject = substFields(subject, data)
            message = substFields(message, data)
            SendMailDialog.sendMail(self, emailTo, subject, message, [self.writtenFileName])


    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        self.createXML()

    @QtCore.pyqtSlot()
    def on_reportButton_clicked(self):
        fsize=os.path.getsize(self.writtenFileName)
        md5=calcCheckSum(self.writtenFileName)
        rep=CF12_D_3_MReport(
            self, self.writtenFileName, fsize, md5, self.params)
        rep.exec_()


class CF12_D_3_MReport(CReportViewDialog):
    def __init__(self, parent, fname, fsize, md5, params):
        CReportViewDialog.__init__(self, parent)
        self.fname=fname
        self.fsize=fsize
        self.md5=md5
        self.begDate=params.get('begDate', QtCore.QDate())
        self.endDate=params.get('endDate', QtCore.QDate())
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            object = self.build()
        finally:
            QtGui.qApp.restoreOverrideCursor()
        self.setWindowTitle(u'Акт приёма-передачи')
        self.setText(object)


    def build(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        text0=u'''Акт приёма-передачи
файла со сведениями о результатах дополнительной диспансеризации
'''

        cursor.setCharFormat(CReportBase.ReportBody)
        text0+=u'\nза период с '+self.begDate.toString('dd.MM.yyyy')+ \
                u' по '+self.endDate.toString('dd.MM.yyyy')+u'\n'

        cursor.insertText(text0)
        cursor.insertBlock()

        tableColumns = [
            ('20%', [u'Имя файла'], CReportBase.AlignLeft),
            ('10%', [u'Размер файла (байт)'], CReportBase.AlignLeft),
            ('20%', [u'Контрольная сумма'], CReportBase.AlignLeft),
            ('20%', [u'Дата создания'], CReportBase.AlignRight),
                       ]

        table = createTable(cursor, tableColumns)

        i = table.addRow()
        table.setText(i, 0, self.fname)
        table.setText(i, 1, str(self.fsize))
        table.setText(i, 2, str(self.md5))
        table.setText(i, 3, datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        text1=''

        my_org_id = QtGui.qApp.currentOrgId()
        org_info = getOrganisationInfo(my_org_id)

        if org_info:
            text1+=u'\n\nЛПУ: '+org_info['shortName']+u' (ИНН '+org_info['INN']+ \
                        u', КПП '+org_info['KPP']+u', ОГРН '+org_info['OGRN']+u')\n'

        cursor.insertText(text1)
        return doc


class CReportF12_D_3_MSetupDialog(CDialogBase, Ui_ReportF12_D_3_MSetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Ф12-Д-3-М')

    def preSetupUi(self):
        pass

    def postSetupUi(self):
        self.cmbEventType.setTable('EventType', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.chkOnlyPermanentAttach.setChecked(params.get('onlyPermanentAttach', False))
        self.chkOnlyPayedEvents.setChecked(params.get('onlyPayedEvents', False))
        self.sbCol3.setValue(forceInt(params.get('tbl1000Col3', 0)))
        self.sbCol4.setValue(forceInt(params.get('tbl1000Col4', 0)))
        self.sbCol5.setValue(forceInt(params.get('tbl1000Col5', 0)))
        self.sbCol6.setValue(forceInt(params.get('tbl1000Col6', 0)))
        self.sbCol7.setValue(forceInt(params.get('tbl1000Col7', 0)))
        self.sbCol8.setValue(forceInt(params.get('tbl1000Col8', 0)))
        self.sbTable2000Col3.setValue(forceInt(params.get('tbl2000Col3', 0)))
        #self.sbNotComplete.setValue(forceInt(params.get('NotComplete', 0)))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['onlyPermanentAttach'] = self.chkOnlyPermanentAttach.isChecked()
        result['onlyPayedEvents'] = self.chkOnlyPayedEvents.isChecked()
        result['tbl1000Col3'] = self.sbCol3.value()
        result['tbl1000Col4'] = self.sbCol4.value()
        result['tbl1000Col5'] = self.sbCol5.value()
        result['tbl1000Col6'] = self.sbCol6.value()
        result['tbl1000Col7'] = self.sbCol7.value()
        result['tbl1000Col8'] = self.sbCol8.value()
        result['tbl2000Col3'] = self.sbTable2000Col3.value()
        #result['NotComplete'] = self.sbNotComplete.value()
        return result

class CMyXmlStreamWriter(QtCore.QXmlStreamWriter):
    def __init__(self,  parent):
        QtCore.QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.nameSpace = u'http://schemas.microsoft.com/office/infopath/2003/myXSD/2008-07-16T06:56:43'

    def writeTextElement(self, elementName, val, len=None):
        if val is None:
            text = ''
        elif not isinstance(val, basestring):
            text = unicode(val)
        else:
            text = val
        if len:
            text = val[:len]
        QtCore.QXmlStreamWriter.writeTextElement(self, self.nameSpace, elementName, text)


    def formatDate(self, date):
        return forceDate(date).toString('dd.MM.yyyy') if date else ''


    def writeStartElement(self, str):
        return QtCore.QXmlStreamWriter.writeStartElement(self, self.nameSpace, str)

    def writeAttribute(self, attrib,  val):
        return QtCore.QXmlStreamWriter.writeAttribute(self, self.nameSpace, attrib,  val)

    def writeFile(self, device, params, t2000, t3000):
        try:
            self.setDevice(device)
            self.writeStartDocument()
            self.writeProcessingInstruction('mso-infoPathSolution',
                'name="urn:schemas-microsoft-com:office:infopath:S7e2m---4n0l--12-D-3-L:-myXSD-2008-07-16T06-56-43" ' \
                'solutionVersion="1.0.0.375" productVersion="12.0.0.0" PIVersion="1.0.0.0" ' \
                'href="http://portal.zdrav/dd/DocLib/Forms/template.xsn"')
            self.writeProcessingInstruction('mso-application', 'progid="InfoPath.Document"' \
                ' versionProgid="InfoPath.Document.2"')
            self.writeNamespace('http://www.w3.org/2001/XMLSchema-instance',  'xsi')
            self.writeNamespace('http://schemas.microsoft.com/office/infopath/2003/dataFormSolution' , 'dfs')
            self.writeNamespace('http://tempuri.org/' ,'tns')
            self.writeNamespace('http://schemas.microsoft.com/office/infopath/2003/changeTracking' , '_xdns0')
            self.writeNamespace('http://schemas.xmlsoap.org/soap/envelope/' ,  'soap')
            self.writeNamespace('urn:schemas-microsoft-com:xml-diffgram-v1' ,  'diffgr')
            self.writeNamespace('urn:schemas-microsoft-com:xml-msdata' ,  'msdata')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/http/' , 'http')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/soap12/' , 'soap12')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/mime/' , 'mime')
            self.writeNamespace('http://schemas.xmlsoap.org/soap/encoding/' , 'soapenc')
            self.writeNamespace('http://microsoft.com/wsdl/mime/textMatching/' , 'tm')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/soap/' , 'ns1')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/' , 'wsdl')
            self.writeNamespace(self.nameSpace,'my')
            self.writeNamespace('http://schemas.microsoft.com/office/infopath/2003', 'xd')
#            self.writeNamespace('uuid:BDC6E3F0-6DA3-11d1-A2A3-00AA00C14882' ,  's')
#            self.writeNamespace('uuid:C2F41010-65B3-11d1-A29F-00AA00C14882' ,  'dt')
#            self.writeNamespace('urn:schemas-microsoft-com:rowset' ,  'rs')
#            self.writeNamespace('#RowsetSchema' , 'z')
            self.writeStartElement(u'form')
            self.writeAttribute(u'name', u'12-Д-М-3')
            self.writeAttribute(u'project', 'DD')
            self.writeAttribute(u'version', '4')
            QtCore.QXmlStreamWriter.writeAttribute(self, u'xml:lang', 'en-US')

            miacCode = forceString(QtGui.qApp.db.translate('Organisation',
                'id', QtGui.qApp.currentOrgId(), 'miacCode'))

            if miacCode == '':
                QtGui.QMessageBox.warning(self.parent,
                    u'Экспорт 12-Д-3-М в XML',
                    u'Отсутствует код МИАЦ для вашего ЛПУ.\n'
                    u'Необходимо установить код в:\n'
                    u'"Справочники.Организации.Организаци".',
                    QtGui.QMessageBox.Close)

            email = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'mailAddress', ''))

            if email == '':
                QtGui.QMessageBox.warning(self.parent,
                    u'Экспорт 12-Д-3-М в XML',
                    u'Отсутствует адрес электронной почты.\n'
                    u'Необходимо установить адрес в:\n'
                    u'"Настройки.Умолчания.e-mail".',
                    QtGui.QMessageBox.Close)

            countDone, countContinued, countByGroup = t2000

            self.writeStartElement(u'LPU')
            self.writeAttribute('lpu_id',  miacCode)
            self.writeAttribute('email',  email)
            self.writeEndElement() # LPU
            self.writeStartElement('data')
            self.writeAttribute('period', forceString(params.get('endDate', QtCore.QDate()).month()))

            self.writeStartElement('DD1000')
            self.writeTextElement('Complete', forceString(params.get('tbl1000Col4', 0)))
            #self.writeTextElement('NotComplete', forceString(params.get('NotComplete', 0)))
            self.writeStartElement('ORDER_DD')
            self.writeTextElement('NoEquipment', forceString(params.get('tbl1000Col5', 0)))
            self.writeTextElement('NoExpert', forceString(params.get('tbl1000Col6', 0)))
            self.writeTextElement('NoEqNEx', forceString(params.get('tbl1000Col7', 0)))
            self.writeEndElement() # ORDER_DD
            self.writeTextElement('AttachedOrgs', forceString(params.get('tbl1000Col3', 0)))
            self.writeTextElement('Summary', forceString(params.get('tbl1000Col8', 0)))
            self.writeEndElement() # DD1000

            self.writeStartElement('DD2000')
            self.writeStartElement('citizen')
            self.writeTextElement('observable', forceString(params.get('tbl2000Col3', 0)))
            self.writeTextElement('observated_complete', forceString(countDone))
            self.writeTextElement('observated_incomplete', forceString(countContinued))
            self.writeEndElement() # citizen
            self.writeStartElement('groups')
            self.writeTextElement('healthy', forceString(countByGroup[0]))
            self.writeTextElement('risk_II', forceString(countByGroup[1]))
            self.writeTextElement('risk_III', forceString(countByGroup[2]))
            self.writeTextElement('risk_VI', forceString(countByGroup[3]))
            self.writeTextElement('risk_V', forceString(countByGroup[4]))
            self.writeEndElement() # groups
            self.writeEndElement() # DD2000

            self.writeStartElement('DD3000')
            self.writeTextElement('A15-A19', forceString(t3000['A15-A19']))
            self.writeStartElement('malignant')
            self.writeTextElement('C15-C26', forceString(t3000['C15-C26']))
            self.writeTextElement('C33-C34', forceString(t3000['C33-C34']))
            self.writeTextElement('C43-C44', forceString(t3000['C43-C44']))
            self.writeTextElement('C50', forceString(t3000['C50']))
            self.writeTextElement('C50-C58', forceString(t3000['C50-C58']))
            self.writeTextElement('C61', forceString(t3000['C61']))
            self.writeTextElement('C81', forceString(t3000['C81-C96']))
            self.writeTextElement('D50-D64', forceString(t3000['D50-D64']))
            self.writeTextElement('E10-E14', forceString(t3000['E10-E14']))
            self.writeTextElement('E66', forceString(t3000['E66']))
            self.writeTextElement('E78', forceString(t3000['E78']))
            self.writeTextElement('I10-I15', forceString(t3000['I10-I15']))
            self.writeTextElement('I20-I25', forceString(t3000['I20-I25']))
            self.writeTextElement('R73', forceString(t3000['R73']))
            self.writeTextElement('R91', forceString(t3000['R91']))
            self.writeTextElement('R92', forceString(t3000['R92']))
            self.writeTextElement('R94.3', forceString(t3000['R94.3']))
            self.writeEndElement() # malignant
            self.writeEndElement() # DD3000

            self.writeEndElement() # data
            self.writeEndElement() # form
            self.writeEndDocument()

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False

        return True
