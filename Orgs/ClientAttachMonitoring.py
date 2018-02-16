# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Exchange.R23.attach.Utils import CAttachSentToTFOMS
from library.DialogBase import CConstructHelperMixin
from library.PreferencesMixin import CContainerPreferencesMixin
from library.TableModel import CCol, CDesignationCol, CTableModel, CTextCol
from library.TreeModel import CDBTreeModel
from .Ui_ClientAttachMonitoring import Ui_ClientAttachMonitoring
from .Utils import CAttachType, getDetailedAttachedCount, getOrganisationSections


class CAttachedCountCol(CCol):
    def __init__(self, title, fields, defaultWidth, colIndex, alignment='l', **params):
        CCol.__init__(self, title, fields, defaultWidth, alignment, **params)
        self._colIndex = colIndex

    def load(self, orgStructureId):
        cnt = getDetailedAttachedCount(orgStructureId, colDescr=[
            (None, None),
            (CAttachType.Territorial, None),
            (CAttachType.Attached, None),
            (None, CAttachSentToTFOMS.NotSynced)
        ])
        self.putIntoCache(orgStructureId, cnt)

    def getFromCache(self, key):
        counts = CCol.getFromCache(self, key)
        return counts[self._colIndex]


class COrgStructureAttachModel(CTableModel):
    def __init__(self, parent):
        self._attachedCache = {}
        self._attachCountCol = CAttachedCountCol(u'Кол-во прикрепленного населения',
                                                 ['id'], 10, colIndex=0, cache=self._attachedCache)
        self._territorialCountCol = CAttachedCountCol(u'Кол-во пациентов по территориальному типу',
                                                      ['id'], 10, colIndex=1, cache=self._attachedCache)
        self._attachedCountCol = CAttachedCountCol(u'Кол-во пациентов по заявлению',
                                                   ['id'], 10, colIndex=2, cache=self._attachedCache)
        self._notSyncedCol = CAttachedCountCol(u'Кол-во несинхронизированного населения',
                                               ['id'], 10, colIndex=3, cache=self._attachedCache,
                                               enabled=QtGui.qApp.isKrasnodarRegion())

        super(COrgStructureAttachModel, self).__init__(parent, cols=[
            CDesignationCol(u'ЛПУ', ['organisation_id'], ('Organisation', 'infisCode'), 5),
            CTextCol(u'Код', ['code'], 40),
            CTextCol(u'Наименование', ['name'], 40),
            self._attachCountCol,
            self._notSyncedCol,
            self._territorialCountCol,
            self._attachedCountCol,
        ], tableName='OrgStructure')

    def clearCache(self):
        self._attachedCache.clear()


class CClientAttachMonitoring(QtGui.QWidget, CContainerPreferencesMixin, CConstructHelperMixin, Ui_ClientAttachMonitoring):
    u""" Дерево и таблица подразделений с кол-вом прикрепленных к ним """

    def __init__(self, parent):
        super(CClientAttachMonitoring, self).__init__(parent)
        self.db = QtGui.qApp.db
        self._orgSections = None
        self._orgStructureOrder = ['organisation_id', 'parent_id', 'code', 'name']
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()

    def preSetupUi(self):
        self.addModels('Tree', CDBTreeModel(self, 'OrgStructure', 'id', 'parent_id', 'name', self._orgStructureOrder, filters=self.getOrgStructureSectionFilter()))
        self.addModels('Table', COrgStructureAttachModel(self))

    def postSetupUi(self):
        self.setModels(self.treeOrgStructure, self.modelTree, self.selectionModelTree)
        self.setModels(self.tblOrgStructure, self.modelTable, self.selectionModelTable)
        self.treeOrgStructure.header().hide()
        self.treeOrgStructure.expandAll()

        idList = self.selectOrgStructures()
        self.modelTable.setIdList(idList)
        self.tblOrgStructure.selectRow(0)

    def clearCache(self):
        self.modelTable.clearCache()

    def _getOrgSections(self):
        if self._orgSections is None:
            self._orgSections = getOrganisationSections()
        return self._orgSections

    def getOrgStructureSectionFilter(self):
        return self.db.makeField('id').inlist(self._getOrgSections())

    def selectOrgStructures(self):
        tableOS = self.modelTable.table()
        groupId = self.currentGroupId()
        cond = [
            tableOS['parent_id'].eq(groupId),
            tableOS['id'].inlist(self._getOrgSections()),
        ]
        return self.db.getIdList(tableOS, tableOS['id'], cond, self._orgStructureOrder)

    def currentGroupId(self):
        return self.modelTree.itemId(self.treeOrgStructure.currentIndex())

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        self.updateTable(None)

    def updateTable(self, itemId=None):
        if not itemId:
            itemId = self.tblOrgStructure.currentItemId()
        idList = self.selectOrgStructures()
        self.tblOrgStructure.setIdList(idList, itemId)
