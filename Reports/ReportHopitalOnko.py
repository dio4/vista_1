# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.ListModel import CListModel
from library.Utils import forceInt, forceString, forceDateTime
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportHospitalOnkoSetupDialog import  Ui_ReportHospitalOnkoSetupDialog


def selectData(params):
    db = QtGui.qApp.db
    stmt = u"""
    select
		e.isPrimary,
		orgS.id as orgStructure_id,
		c.id as client_id,
		e.id as event_id,
		e.execDate,
		ds.MKB
	from Client c
		inner join Event e
			on e.client_id = c.id
		inner join EventType et
			on et.id = e.eventType_id
		inner join Visit v
			on v.event_id = e.id
		inner join rbService s
			on s.id = v.service_id
		inner join Person p
			on p.id = e.execPerson_id
		inner join OrgStructure orgS
			on orgS.id = p.orgStructure_id

		left join Diagnostic dc
			on dc.event_id = e.id
		left join Diagnosis ds
			on ds.id = dc.diagnosis_id
	where
		et.code = '01'
		and s.code = 'аОнкол'
		and e.deleted = 0
        and e.execDate >= '2016-01-01'
        Order by c.id, e.isPrimary, ds.MKB, e.execDate
    """
    query = db.query(stmt)
    return query


class CReportHospitalOnko(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Госпитализация амбулаторных пациентов')

    def getSetupDialog(self, parent):
        result = CReportHospitalOnkoDialog(parent)
        result.setTitle(self.title())
        return result

    def getDescription(self, params):
        rows = CReport.getDescription(self, params)

        diagnosis = params.get('diagnosis', 0)
        sex = params.get('sex', 0)
        age = params.get('age', 0)
        citizenship = params.get('citizenship', 0)
        orgStructure = params.get('orgStructure', 0)

        if diagnosis:
            rows.append(u'диагноз: %s' % CDiagnosisModel.list[diagnosis])
        # if sex:
        #     rows.append(u'Пол: %s' % CSexModel.list[sex])  # дублируется с родительским
        if age:
            rows.append(u'возраст: %s' % CAgeModel.list[age])
        if citizenship:
            rows.append(u'житель: %s' % CCitizenshipModel.list[citizenship])
        if orgStructure:
            rows.append(u'подразделение: %s' % COrgStructureModel.list[orgStructure])

        return rows

    def getData(self, query, params):
        data = {}
        while query.next():
            record = query.record()
            clientId = forceInt(record.value('client_id'))
            eventId = forceInt(record.value('event_id'))
            isPrimary = forceInt(record.value('isPrimary'))
            orgStructureId = forceInt(record.value('orgStructure_id'))
            execDate = forceDateTime(record.value('execDate'))
            MKB = forceString(record.value('MKB'))[:3]
            data.setdefault(clientId, []).append(
                {'eventId': eventId,
                 'isPrimary': isPrimary,
                 'orgStructureId': orgStructureId,
                 'execDate': execDate,
                 'MKB': MKB})
        sortedData = {}
        for clientId, eventList in data.iteritems():
            primaryFound = False
            for event in eventList:
                if not event.get('isPrimary') in [1, 2]:
                    continue
                if event.get('isPrimary') == 2 and not event.get('MKB'):
                    continue
                if primaryFound and event.get('isPrimary') == 1:
                    continue
                if not primaryFound and event.get('isPrimary') == 1:
                    primaryFound = True
                    sortedData.setdefault(clientId, {}).setdefault(event.get('MKB'), event)
                if event.get('isPrimary') == 2:
                    sortedData.setdefault(clientId, {}).setdefault(event.get('MKB'), event)
        for clientId in sortedData.iterkeys():
            if u'' in sortedData[clientId] and len(sortedData[clientId]) > 2:
                sortedData[clientId].pop(u'')
            if u'' in sortedData[clientId] and len(sortedData[clientId]) == 2:
                sortedData[clientId][u'']['MKB'] = sortedData[clientId][sortedData[clientId].keys()[1]]['MKB']
                sortedData[clientId][u'']['isPrimary'] = 2
                sortedData[clientId].pop(sortedData[clientId].keys()[1])
        self.createTempTable(sortedData)
        hospitalData = self.getHospitalData(params)
        return hospitalData

    def createTempTable(self, data):
        db = QtGui.qApp.db
        stmt = u"""
        Drop temporary table if exists tmpList;
        Create temporary table tmpList
        (
            id int(11) not null auto_increment,
            isPrimary tinyint(1),
            MKB varchar(10) default '',
            client_id int(11) default NUll,
            orgStructure_id int(11) default null,
            execDate date,
            Primary key(id)
        );
        """
        valueList = []
        for clientId, MKBs in data.iteritems():
            for MKB, item in MKBs.iteritems():
                valueList.append(u"('%s', '%s', '%s', '%s', '%s')" % (forceString(item['isPrimary']), MKB, forceString(clientId), forceString(item['orgStructureId']), item['execDate'].toString('yyyy-MM-dd')))
        if valueList:
            stmt = stmt + u"""\nInsert into tmpList (isPrimary, MKB, client_id, orgStructure_id, execDate)
            values """ + u',\n'.join(valueList) + u';'
        db.query(stmt)

    def getHospitalData(self, params):
        db = QtGui.qApp.db
        tableClient = db.table('Client').alias('c')
        tableTemp = db.table('tmpList').alias('t')
        sex = params.get('sex', 0)
        age = params.get('age', 0)
        diagnosis = params.get('diagnosis', 0)
        citizenship = params.get('citizenship', 0)
        orgStructure = params.get('orgStructure', 0)
        orgStructureId = COrgStructureModel.getOrgStructureId(orgStructure)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        join = ''
        cond = []
        if begDate:
            cond.append(tableTemp['execDate'].ge(begDate))
        if endDate:
            cond.append(tableTemp['execDate'].le(endDate))
        if sex:
            cond.append(tableClient['sex'].eq(sex))

        if age == 1:
            cond.append(u"((YEAR(t.execDate)-YEAR(c.birthDate)) - (RIGHT(t.execDate,5)<RIGHT(c.birthDate,5))) < 18")
        elif age == 2:
            cond.append(db.joinAnd([
            u"((YEAR(t.execDate)-YEAR(c.birthDate)) - (RIGHT(t.execDate,5)<RIGHT(c.birthDate,5))) > 18",
            db.joinOr([
                u"c.sex = '1' AND ((YEAR(t.execDate)-YEAR(c.birthDate)) - (RIGHT(t.execDate,5)<RIGHT(c.birthDate,5))) < 60",
                u"c.sex = '2' AND ((YEAR(t.execDate)-YEAR(c.birthDate)) - (RIGHT(t.execDate,5)<RIGHT(c.birthDate,5))) < 55"])
            ]))
        elif age == 3:
            cond.append(db.joinOr([
                u"c.sex = '1' AND ((YEAR(t.execDate)-YEAR(c.birthDate)) - (RIGHT(t.execDate,5)<RIGHT(c.birthDate,5))) >= 60",
                u"c.sex = '2' AND ((YEAR(t.execDate)-YEAR(c.birthDate)) - (RIGHT(t.execDate,5)<RIGHT(c.birthDate,5))) >= 55"])
            )
        if diagnosis == 1:
            cond.append(db.joinAnd([
                tableTemp['isPrimary'].eq(2),
                tableTemp['MKB'].ne(u"''")]))

        if citizenship in [1, 2, 3]:
            join = u'''
                INNER JOIN
            ClientAddress ca ON ca.id = GETCLIENTREGADDRESSID(c.id)
                INNER JOIN
            Address a ON ca.address_id = a.id
                INNER JOIN
            AddressHouse ah ON ah.id = a.house_id
                INNER JOIN
            kladr.KLADR k ON k.CODE = ah.KLADRCode
            '''
        if citizenship == 1:
            cond.append(u"k.CODE = '7800000000000'")
        elif citizenship == 2:
            cond.append(u"k.CODE like '47%%'")
        elif citizenship == 3:
            cond.append(u"k.SOCR in ('п', 'с', 'д', 'пгт')")
        elif citizenship == 4:
            join= u'''
                INNER JOIN
            ClientDocument cd ON cd.id = GETCLIENTDOCUMENTID(c.id)
                INNER JOIN
            rbDocumentType dt ON dt.id = cd.documentType_id
            '''
            cond.append(u"dt.name = 'ИНПАСПОРТ'")
        if orgStructureId:
            list = getOrgStructureDescendants(orgStructureId)
            if list:
                cond.append(u"t.orgStructure_id in (%s)" % u', '.join([u"'%d'" % id for id in list]))
            else:
                cond.append(u"t.orgStructure_id in ('0')")
        stmt = u"""
        SELECT
            t.isPrimary,
            t.MKB,
            t.client_id,
            t.orgStructure_id,
            t.execDate,
            IF((SELECT
                e.id
            FROM
                Event e
            INNER JOIN EventType et ON et.id = e.eventType_id
            INNER JOIN Diagnostic dc ON dc.event_id = e.id
            INNER JOIN Diagnosis ds ON ds.id = dc.diagnosis_id
            WHERE
                et.code = '03'
                    AND e.client_id = t.client_id
                    AND DATE_ADD(e.execDate, INTERVAL 2 MONTH) > DATE(t.execDate)
                    AND ds.MKB LIKE 'C%%'
                    AND (t.MKB = '' OR ds.MKB = t.MKB)
            ORDER BY e.execDate
            LIMIT 1) is not null, 1, 0) as hasHospital
        FROM
            tmpList t
            INNER JOIN Client c ON c.id = t.client_id
            %s
        WHERE %s
        """ % (join, db.joinAnd(cond))
        query = db.query(stmt)
        data = {}
        while query.next():
            record = query.record()
            clientId = forceInt(record.value('client_id'))
            eventId = forceInt(record.value('event_id'))
            isPrimary = forceInt(record.value('isPrimary'))
            orgStructureId = forceInt(record.value('orgStructure_id'))
            execDate = forceDateTime(record.value('execDate'))
            MKB = forceString(record.value('MKB'))[:3]
            hasHospital = forceInt(record.value('hasHospital'))

            data.setdefault(clientId, {})[MKB] = {
                'eventId': eventId,
                'isPrimary': isPrimary,
                'orgStructureId': orgStructureId,
                'execDate': execDate,
                'hasHospital': hasHospital,
                'MKB': MKB
            }
        return data

    def countData(self, data, params):
        orgStructureIndex = params.get('orgStructure', 0)
        orgStructures = [COrgStructureModel.getOrgStructureCode(orgStructureIndex)] if orgStructureIndex else COrgStructureModel.list[1:]
        result = [(COrgStructureModel.idMap[code], [code] + [0] * 5) for code in orgStructures]
        # result = [
        #     (152, [u'КДО', 0, 0, 0, 0, 0]),  # Клинико-диагностическое отделение
        #     (414, [u'КДЦ', 0, 0, 0, 0, 0]),  # Медицинский центр (Консультативно-диагностическое подразделение)
        #     (576, [u'ЦДЛ', 0, 0, 0, 0, 0])  # Центр лечения и профилактики (Консультативно-диагностическое подразделение)
        # ]

        orgStructureDescendants = dict([(id, getOrgStructureDescendants(id)) for id, row in result])

        orgStructureMapRow = {}
        for i, (headId, row) in enumerate(result):
            orgStructureMapRow[headId] = i
            for id in getOrgStructureDescendants(headId):
                orgStructureMapRow[id] = i

        for clientId, events in data.iteritems():
            for MKB in events.itervalues():
                tmp = [u'', 0, 0, 0, 0, 0]
                tmp[1] += 1
                if MKB['MKB'] and MKB['MKB'][0] == u'C':
                    tmp[2] += 1
                    if MKB['isPrimary'] == 2:
                        tmp[3] += 1
                    if MKB['hasHospital']:
                        tmp[4] += 1
                        if MKB['isPrimary'] == 2:
                            tmp[5] += 1
                for orgStructureId, list in orgStructureDescendants.iteritems():
                    if MKB['orgStructureId'] in list:
                        for idx in range(1, len(tmp)):
                            result[orgStructureMapRow[orgStructureId]][1][idx] += tmp[idx]

        totalRow = [u'ИТОГО', 0, 0, 0, 0, 0]
        for id, row in result:
            for idx in xrange(1, len(totalRow)):
                totalRow[idx] += row[idx]
        result.append((None, totalRow))

        return result


    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%',  [u''], CReportBase.AlignLeft),
                        ('%',  [u'Обратилось амбулаторно', u'Всего'], CReportBase.AlignLeft),
                        ('%',  [u'', u'Из них онкология C00-C99', u'Всего'], CReportBase.AlignLeft),
                        ('%',   [u'', u'', u'Впервые выявлено в НИИ онкологии'], CReportBase.AlignLeft),
                        ('%',   [u'Из них госпитализировано', u'Всего'], CReportBase.AlignLeft),
                        ('%',   [u'', u'Д-з впервые выявлен в НИИ онкологии'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 3)
        table.mergeCells(1, 1, 2, 1)
        table.mergeCells(1, 2, 1, 2)
        table.mergeCells(0, 4, 1, 2)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(1, 5, 2, 1)

        data = self.getData(query, params)
        result = self.countData(data, params)
        for id, row in result:
            i = table.addRow()
            table.setText(i, 0, row[0], fontBold=True)
            for col, value in enumerate(row[1:]):
                table.setText(i, col+1, value)
        return doc


class CDiagnosisModel(CListModel):
    list = [u'Все', u'Впервые выявленные в НИИ онкологии']
    def __init__(self):
        CListModel.__init__(self, CDiagnosisModel.list)


class CSexModel(CListModel):
    list = [u'Все', u'Мужской', u'Женский']
    def __init__(self):
        CListModel.__init__(self, CSexModel.list)


class CAgeModel(CListModel):
    list = [u'Все', u'Дети', u'Лица трудоспособного возраста', u'Лица старше трудоспособного возраста']
    def __init__(self):
        CListModel.__init__(self, CAgeModel.list)


class CCitizenshipModel(CListModel):
    list = [u'Все', u'Жители СПб', u'Иногородние', u'Жители села', u'Иностранцы']
    def __init__(self):
        CListModel.__init__(self, CCitizenshipModel.list)


class COrgStructureModel(CListModel):
    list = [u'ЛПУ', u'КДО', u'КДЦ', u'ЦДЛ']
    idList = [None, 152, 414, 576]
    idMap = dict([(code, id) for code, id in zip(list, idList)])

    def __init__(self):
        CListModel.__init__(self, COrgStructureModel.list)

    @staticmethod
    def getOrgStructureId(index):
        return COrgStructureModel.idList[index]

    @staticmethod
    def getOrgStructureCode(index):
        return COrgStructureModel.list[index]


class CReportHospitalOnkoDialog(CDialogBase, Ui_ReportHospitalOnkoSetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.addModels('Diagnosis', CDiagnosisModel())
        self.addModels('Sex', CSexModel())
        self.addModels('Age', CAgeModel())
        self.addModels('Citizenship', CCitizenshipModel())
        self.addModels('OrgStructure', COrgStructureModel())
        self.cmbDiagnosis.setModel(self.modelDiagnosis)
        self.cmbSex.setModel(self.modelSex)
        self.cmbAge.setModel(self.modelAge)
        self.cmbCitizenship.setModel(self.modelCitizenship)
        self.cmbOrgStructure.setModel(self.modelOrgStructure)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbDiagnosis.setCurrentIndex(params.get('diagnosis', 0))
        self.cmbAge.setCurrentIndex(params.get('age', 0))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.cmbCitizenship.setCurrentIndex(params.get('citizenship', 0))
        self.cmbOrgStructure.setCurrentIndex(params.get('orgStructure', 0))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['diagnosis'] = self.cmbDiagnosis.currentIndex()
        params['age'] = self.cmbAge.currentIndex()
        params['sex'] = self.cmbSex.currentIndex()
        params['citizenship'] = self.cmbCitizenship.currentIndex()
        params['orgStructure'] = self.cmbOrgStructure.currentIndex()
        return params

