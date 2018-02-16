# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from library.Utils import forceBool, forceRef, forceString
from .Utils import COrgStructureAreaInfo, getAttachedCount


class CAttachedClientsCountReport(CReport):
    def __init__(self, parent):
        super(CAttachedClientsCountReport, self).__init__(parent)
        self.setTitle(u'Количество прикрепленного населения')
        self.db = QtGui.qApp.db
        self._orgSections = None

    def getSetupDialog(self, parent):
        return None

    def _getOrgSections(self):
        u""" Список всех подразделений, являющихся участками, либо содержащих участки в своей структуре """
        if self._orgSections is None:
            tableOrgStructure = self.db.table('OrgStructure')
            cols = [
                tableOrgStructure['id'],
                self.db.func.getOrgStructurePath(tableOrgStructure['id']).alias('path')
            ]
            cond = [
                tableOrgStructure['organisation_id'].eq(QtGui.qApp.currentOrgId()),
                tableOrgStructure['isArea'].ne(COrgStructureAreaInfo.No),
                tableOrgStructure['deleted'].eq(0),
            ]
            sections = set()
            for rec in self.db.iterRecordList(tableOrgStructure, cols, cond):
                sections.add(forceRef(rec.value('id')))
                sections |= set(int(id_str) for id_str in forceString(rec.value('path')).split('.') if id_str)
            self._orgSections = list(sections)
        return self._orgSections

    def getReportData(self, orgStructureIdList):
        db = self.db
        tableOrgStructure = db.table('OrgStructure')

        orgStructurePath = db.func.getOrgStructurePath(tableOrgStructure['id'])
        cols = [
            tableOrgStructure['id'],
            tableOrgStructure['name'],
            db.makeField(tableOrgStructure['isArea'].ne(COrgStructureAreaInfo.No)).alias('isArea'),
            orgStructurePath.alias('path')
        ]
        cond = [
            tableOrgStructure['id'].inlist(orgStructureIdList)
        ]
        order = [
            orgStructurePath.desc(),
            tableOrgStructure['name']
        ]

        isArea = {}
        name = {}
        count = {}
        path = {}
        for rec in db.iterRecordList(tableOrgStructure, cols, cond, order=order):
            orgStructureId = forceRef(rec.value('id'))
            path[orgStructureId] = forceString(rec.value('path'))
            isArea[orgStructureId] = forceBool(rec.value('isArea'))
            name[orgStructureId] = forceString(rec.value('name'))
            count[orgStructureId] = getAttachedCount(orgStructureId)

        idList = sorted(count.keys(), key=lambda orgStructureId: (-path[orgStructureId].count('.'),
                                                                  name[orgStructureId]))
        return [(isArea[orgStructureId],
                 name[orgStructureId],
                 count[orgStructureId]) for orgStructureId in idList]

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        tableColumns = [
            ('50%', [u'Участок'], CReportBase.AlignLeft),
            ('25%', [u'Количество прикрепленного населения'], CReportBase.AlignRight)
        ]
        table = createTable(cursor, tableColumns)

        fmt = CReportBase.ReportBody
        fmtBold = CReportBase.TableTotal

        for isArea, name, count in self.getReportData(self._getOrgSections()):
            i = table.addRow()
            table.setText(i, 0, name, charFormat=fmt if isArea else fmtBold)
            table.setText(i, 1, count)
        return doc
