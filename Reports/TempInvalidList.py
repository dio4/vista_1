# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Registry.Utils import getClientInfo, getClientPhonesEx
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_TempInvalidSetup import Ui_TempInvalidSetupDialog
from library.DialogBase import CDialogBase
from library.Utils import forceDate, forceInt, forceRef, forceString, getVal, calcAge, formatDate, formatName, \
    formatSex, formatSNILS
from library.database import addDateInRange


def selectData(
        begDate, endDate, byPeriod, doctype, tempInvalidReasonId, onlyClosed, orgStructureId, personId, durationFrom,
        durationTo, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, MKBFilter,
        MKBFrom, MKBTo, insuranceOfficeMark
):
    stmt = """
SELECT
   TempInvalid.client_id,
   prev_id,
   serial,
   number,
   TempInvalid.caseBegDate,
   TempInvalid.begDate,
   TempInvalid.endDate,
   duration,
   Diagnosis.MKB,
   rbTempInvalidReason.code,
   (
        SELECT CONCAT_WS(' - ', cd.serial, cd.number) AS doc
        FROM ClientDocument cd INNER JOIN rbDocumentType rb ON rb.id = cd.documentType_id
        WHERE cd.client_id = Client.id AND rb.code = '14' AND cd.deleted = 0
        ORDER BY cd.date DESC
        LIMIT 1
   ) AS doc,
   (
        SELECT IF(cw.org_id IS NOT NULL, o.shortName, IF(LENGTH(cw.freeInput) > 0, cw.freeInput, '-')) AS work
        FROM ClientWork cw LEFT JOIN Organisation o ON o.id = cw.org_id
        WHERE cw.client_id = Client.id AND cw.deleted = 0
        ORDER BY cw.id DESC
        LIMIT 1
   ) AS work
   FROM TempInvalid
   LEFT JOIN Diagnosis ON Diagnosis.id = TempInvalid.diagnosis_id
   LEFT JOIN Person    ON Person.id = TempInvalid.person_id
   LEFT JOIN rbTempInvalidReason ON rbTempInvalidReason.id = TempInvalid.tempInvalidReason_id
   LEFT JOIN Client    ON Client.id = TempInvalid.client_id
WHERE
   %s
ORDER BY Client.lastName, Client.firstName, Client.patrName, begDate
    """
    db = QtGui.qApp.db
    table = db.table('TempInvalid')
    tableClient = db.table('Client')
    cond = []
    if doctype:
        cond.append(table['doctype_id'].eq(doctype))
    else:
        cond.append(table['type'].eq(0))
    cond.append(table['deleted'].eq(0))
    if tempInvalidReasonId:
        cond.append(table['tempInvalidReason_id'].eq(tempInvalidReasonId))
    if byPeriod:
        cond.append(table['caseBegDate'].le(endDate))
        cond.append(table['endDate'].ge(begDate))
    else:
        addDateInRange(cond, table['endDate'], begDate, endDate)
    if onlyClosed:
        cond.append(table['closed'].eq(1))
    if orgStructureId:
        tablePerson = db.table('Person')
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if personId:
        cond.append(table['person_id'].eq(personId))
    if durationTo:
        cond.append(table['duration'].ge(durationFrom))
        cond.append(table['duration'].le(durationTo))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('TempInvalid.begDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom)
        cond.append('TempInvalid.begDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (ageTo + 1))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                   + 'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                   + 'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS(' + subStmt + ')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                   + 'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                   + 'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS(' + subStmt + ')')
    if MKBFilter == 1:
        tableDiagnosis = db.table('Diagnosis')
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    elif MKBFilter == 2:
        tableDiagnosis = db.table('Diagnosis')
        cond.append(db.joinOr([tableDiagnosis['MKB'].eq(''), tableDiagnosis['MKB'].isNull()]))
    if insuranceOfficeMark in [1, 2]:
        cond.append(table['insuranceOfficeMark'].eq(insuranceOfficeMark - 1))
    return db.query(stmt % (db.joinAnd(cond)))


class CTempInvalidList(CReport):
    name = u'Список пациентов с ВУТ'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)

    def getSetupDialog(self, parent):
        result = CTempInvalidSetupDialog(parent)
        result.setAnalysisMode(True)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        byPeriod = params.get('byPeriod', False)
        doctype = params.get('doctype', 0)
        tempInvalidReason = params.get('tempInvalidReason', None)
        onlyClosed = params.get('onlyClosed', True)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        durationFrom = params.get('durationFrom', 0)
        durationTo = params.get('durationTo', 0)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        MKBFilter = params.get('MKBFilter', 0)
        MKBFrom = params.get('MKBFrom', '')
        MKBTo = params.get('MKBTo', '')
        insuranceOfficeMark = params.get('insuranceOfficeMark', 0)

        db = QtGui.qApp.db
        tbl = db.table('TempInvalid')
        tblDiag = db.table('Diagnosis')
        tblReas = db.table('rbTempInvalidReason')

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('5%', [u'№'], CReportBase.AlignRight),
            ('5%', [u'код'], CReportBase.AlignLeft),
            ('20%', [u'ФИО,\nдата рождения (возраст),\nпол'], CReportBase.AlignLeft),
            ('25%', [u'Адрес,\nтелефон'], CReportBase.AlignLeft),
            ('10%', [u'Паспортные данные,\nсерия - номер'], CReportBase.AlignLeft),
            ('10%', [u'СНИЛС,\nполис'], CReportBase.AlignLeft),
            ('5%', [u'Шифр МКБ\nТип'], CReportBase.AlignLeft),
            ('5%', [u'Период'], CReportBase.AlignLeft),
            ('5%', [u'Дней'], CReportBase.AlignRight),
            ('5%', [u'Серия\nНомер'], CReportBase.AlignLeft),
            ('5%', [u'Место работы'], CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)
        n = 0
        query = selectData(
            begDate, endDate, byPeriod, doctype, tempInvalidReason, onlyClosed, orgStructureId, personId,
            durationFrom, durationTo, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, MKBFilter, MKBFrom,
            MKBTo, insuranceOfficeMark
        )
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            n += 1
            sumDuration = 0
            record = query.record()
            clientId = forceRef(record.value('client_id'))
            serial = forceString(record.value('serial'))
            number = forceString(record.value('number'))
            caseBegDate = forceDate(record.value('caseBegDate'))
            #            begDate = forceDate(record.value('begDate'))
            endDate = forceDate(record.value('endDate'))
            duration = forceInt(record.value('duration'))
            MKB = forceString(record.value('MKB'))
            work = forceString(record.value('work'))
            document = forceString(record.value('doc'))
            reasonCode = forceString(record.value('code'))
            prev_id = forceInt(record.value('prev_id'))

            info = getClientInfo(clientId)
            name = formatName(info['lastName'], info['firstName'], info['patrName'])
            nameBDateAndSex = '\n'.join([
                name, '%s (%s)' % (formatDate(info['birthDate']), calcAge(info['birthDate'], begDate)),
                formatSex(info['sexCode'])
            ])
            regAddress = getVal(info, 'regAddress', u'не указан')
            locAddress = getVal(info, 'locAddress', u'не указан')
            phones = getClientPhonesEx(clientId)
            addressAndPhone = regAddress if regAddress else ''
            addressAndPhone += '\n' + locAddress if locAddress else ''
            addressAndPhone += '\n' + phones if phones else ''
            SNILSAndPolicy = '\n'.join([formatSNILS(info['SNILS']), getVal(info, 'policy', u'нет')])
            MKBandType = '\n'.join([MKB, reasonCode])
            period = '\n'.join([forceString(caseBegDate), forceString(endDate)])
            serialAndNumber = '\n'.join([serial, number])

            i = table.addRow()
            table.setText(i, 0, n)
            table.setText(i, 1, clientId)
            table.setText(i, 2, nameBDateAndSex)
            table.setText(i, 3, addressAndPhone)
            table.setText(i, 4, document)
            table.setText(i, 5, SNILSAndPolicy)
            table.setText(i, 6, MKBandType)
            table.setText(i, 7, period)
            table.setText(i, 8, duration)
            table.setText(i, 9, serialAndNumber)
            table.setText(i, 10, work)

            if prev_id and onlyClosed:
                sumDuration += duration
                extraRows = 0
                while prev_id:
                    prev_record = db.getRecordEx(
                        tbl,
                        [
                            tbl['begDate'], tbl['endDate'], tbl['duration'], tbl['serial'], tbl['number'],
                            tbl['prev_id'], tbl['diagnosis_id'], tbl['tempInvalidReason_id']
                        ],
                        [tbl['id'].eq(prev_id), tbl['deleted'].eq(0)]
                    )
                    if prev_record:
                        i = table.addRow()
                        extraRows += 1
                        begDate = forceDate(prev_record.value('begDate'))
                        endDate = forceDate(prev_record.value('endDate'))
                        duration = forceInt(prev_record.value('duration'))
                        serial = forceString(prev_record.value('serial'))
                        number = forceString(prev_record.value('number'))
                        prev_id = forceInt(prev_record.value('prev_id'))
                        diagnosis_id = forceInt(prev_record.value('diagnosis_id'))
                        reason_id = forceInt(prev_record.value('tempInvalidReason_id'))
                        MKB = forceString(db.translate(tblDiag, tblDiag['id'], diagnosis_id, tblDiag['MKB']))
                        reason = forceString(db.translate(tblReas, tblReas['id'], reason_id, tblReas['code']))
                        period = '\n'.join([forceString(begDate), forceString(endDate)])
                        serialAndNumber = '\n'.join([serial, number])
                        table.setText(i, 6, MKB + '\n' + reason)
                        table.setText(i, 7, period)
                        table.setText(i, 8, duration)
                        table.setText(i, 9, serialAndNumber)
                        sumDuration += duration
                i = table.addRow()
                extraRows += 1
                table.setText(i, 7, u'')
                table.setText(i, 8, u'Всего дней: ' + unicode(sumDuration))
                table.mergeCells(i - extraRows, 0, extraRows + 1, 1)
                table.mergeCells(i - extraRows, 1, extraRows + 1, 1)
                table.mergeCells(i - extraRows, 2, extraRows + 1, 1)
                table.mergeCells(i - extraRows, 3, extraRows + 1, 1)
                table.mergeCells(i - extraRows, 4, extraRows + 1, 1)
                table.mergeCells(i - extraRows, 5, extraRows + 1, 1)
                table.mergeCells(i, 6, 1, 2)

        return doc


class CTempInvalidSetupDialog(CDialogBase, Ui_TempInvalidSetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setAnalysisMode(False)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        filter = 'type=0'
        self.cmbDoctype.setTable('rbTempInvalidDocument', True, filter)
        self.cmbReason.setTable('rbTempInvalidReason', True, filter)
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.chkOldForm.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setAnalysisMode(self, mode=True):
        for widget in [
            self.lblDuration, self.frmDuration,
            self.lblSex, self.frmSex,
            self.lblAge, self.frmAge,
            self.lblSocStatusClass, self.cmbSocStatusClass,
            self.lblSocStatusType, self.cmbSocStatusType,
            self.lblMKB, self.frmMKB,
        ]:
            widget.setVisible(mode)
        self.analysisMode = True

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.chkByPeriod.setChecked(params.get('byPeriod', False))
        self.cmbDoctype.setValue(params.get('doctype', None))
        self.cmbReason.setValue(params.get('tempInvalidReason', None))
        self.chkOnlyClosed.setChecked(params.get('onlyClosed', True))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.edtDurationFrom.setValue(params.get('durationFrom', 0))
        self.edtDurationTo.setValue(params.get('durationTo', 0))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo', 'Z99.9'))
        self.cmbInsuranceOfficeMark.setCurrentIndex(params.get('insuranceOfficeMark', 0))
        self.chkOldForm.setChecked(params.get('oldForm', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['byPeriod'] = self.chkByPeriod.isChecked()
        result['doctype'] = self.cmbDoctype.value()
        result['tempInvalidReason'] = self.cmbReason.value()
        result['onlyClosed'] = self.chkOnlyClosed.isChecked()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        if self.analysisMode:
            result['durationFrom'] = self.edtDurationFrom.value()
            result['durationTo'] = self.edtDurationTo.value()
            result['sex'] = self.cmbSex.currentIndex()
            result['ageFrom'] = self.edtAgeFrom.value()
            result['ageTo'] = self.edtAgeTo.value()
            result['socStatusClassId'] = self.cmbSocStatusClass.value()
            result['socStatusTypeId'] = self.cmbSocStatusType.value()
            result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
            result['MKBFrom'] = forceString(self.edtMKBFrom.text())
            result['MKBTo'] = forceString(self.edtMKBTo.text())
        result['insuranceOfficeMark'] = self.cmbInsuranceOfficeMark.currentIndex()
        result['oldForm'] = self.chkOldForm.isChecked()
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pacs',
        'port': 3306,
        'database': 's11vm',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CTempInvalidList(None)
    w.exec_()


if __name__ == '__main__':
    main()
