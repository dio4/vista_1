# coding=utf-8
from PyQt4 import QtGui, QtCore

import library.database
from KLADR.KLADRModel import getStreetName
from Orgs.Utils import getOrgStructureDescendants
from library.ListModel import CListModel
from library.TreeModel import CTreeModel, CTreeItemWithId
from library.Utils import forceString, forceInt


class CSelectHouseFromOrgStructureModel(CListModel):
    def __init__(self, parent=None):
        self._orgStructure = None
        CTreeModel.__init__(self, parent, CRootItem(None))
        self.rootItemVisible = False

    def setOrgStructure(self, value):
        self._orgStructure = value
        self._rootItem = CRootItem(value)
        self.reset()

    def orgStructure(self):
        return self._orgStructure


class CRootItem(CListItemWithId):
    def __init__(self, orgStructureId):
        super(CRootItem, self).__init__(None, u'', None)
        self._orgStructureId = orgStructureId

    def loadChildren(self):
        if not self._orgStructureId:
            return []
        items = [CStreetItem(self, u'<все>', (None, None), self._orgStructureId)]
        db = QtGui.qApp.db  # type: library.database.CMySqlDatabase
        tbl_osa = db.table('OrgStructure_Address')
        tbl_ah = db.table('AddressHouse')
        tbl = tbl_osa.innerJoin(tbl_ah, tbl_osa['house_id'].eq(tbl_ah['id']))
        for item in db.getRecordList(tbl,
                                     (tbl_ah['KLADRStreetCode'],),
                                     tbl_osa['master_id'].inlist(getOrgStructureDescendants(self._orgStructureId)),
                                     tbl_ah['KLADRStreetCode'],
                                     True):
            items.append(CStreetItem(self,
                                     getStreetName(forceString(item.value('KLADRStreetCode'))) or u'<пусто>',
                                     (forceString(item.value('KLADRStreetCode')), None),
                                     self._orgStructureId))
        return items


class CStreetItem(CTreeItemWithId):
    def __init__(self, parent, name, itemId, orgStructureId):
        super(CStreetItem, self).__init__(parent, name, itemId)
        self._orgStructureId = orgStructureId

    def loadChildren(self):
        if not self._orgStructureId:
            return []
        items = [CHouseItem(self, u'<все>', (self._id[0], None))]
        db = QtGui.qApp.db  # type: library.database.CMySqlDatabase
        tbl_osa = db.table('OrgStructure_Address')
        tbl_ah = db.table('AddressHouse')
        tbl = tbl_osa.innerJoin(tbl_ah, tbl_osa['house_id'].eq(tbl_ah['id']))
        for item in db.getRecordList(tbl,
                                     (tbl_ah['id'], tbl_ah['number'], tbl_ah['corpus']),
                                     db.joinAnd((
                                         tbl_osa['master_id'].inlist(getOrgStructureDescendants(self._orgStructureId)),
                                         tbl_ah['KLADRStreetCode'].eq(self._id[0])
                                     ))):
            number = forceString(item.value('number'))
            corpus = forceString(item.value('corpus'))
            items.append(CHouseItem(self,
                                    (number + ((u'к' + corpus) if corpus else '')) or u'<пусто>',
                                    (self._id[0], forceInt(item.value('id')))))
        return items


class CHouseItem(CTreeItemWithId):
    def __init__(self, parent, name, itemId):
        super(CHouseItem, self).__init__(parent, name, itemId)

    def loadChildren(self):
        return []
