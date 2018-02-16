# -*- coding: utf-8 -*-

#############################################################################
# #
# # Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
# #
#############################################################################

u"""Модель: Формуляры"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QVariant
from FormularyItemComboBox import CFormularyItemInDocTableCol

from library.InDocTable                 import CInDocTableCol, CEnumInDocTableCol, CRBInDocTableCol, CBoolInDocTableCol, CRecordListModel
from library.Utils                      import forceInt, forceString, forceDouble

class CFormularyModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CRBInDocTableCol(u'Отделение', 'orgStructure_id', 300, 'OrgStructure'))
        self.addCol(CEnumInDocTableCol(u'Тип', 'type', 80, [u'формуляр отделения', u'формуляр расходных материалов', u'формуляр дезсредств', u'формуляр реактивов']))
        self.addCol(CInDocTableCol(u'Дата начала', 'begDate', 70))
        self.addCol(CInDocTableCol(u'Дата окончания', 'endDate', 70))
        self.addCol(CBoolInDocTableCol(u'Активен', 'isActive', 20))

    def idList(self):
        idList = []
        for item in self._items:
            idList.append(forceInt(item.value('id')))
        return idList

    def itemByRow(self, row):
        return self._items[row]

    def loadData(self, doctorMode, params): #date, department, drug, doctorMode):
        from HospitalBeds.HospitalBedsDialog    import getOrgStructureIdList
        self._items = []

        db = QtGui.qApp.db
        tblDrugFormulary = db.table('DrugFormulary').alias('f')
        #tblOrgStructure = db.table('OrgStructure')

        queryTable = tblDrugFormulary #.leftJoin(tblOrgStructure, tblOrgStructure['id'].eq(tblDrugFormulary['orgStructure_id']))

        begDate = params.get('begDate', QtCore.QDate().currentDate())
        #endDate = params.get('endDate', QtCore.QDate().currentDate())
        cond = [
             tblDrugFormulary['endDate'].ge(begDate)

         ]

        if doctorMode:
           cond.append(tblDrugFormulary['type'].eq(0))
        else:
           cond.append(tblDrugFormulary['type'].gt(0))

        cond.append(tblDrugFormulary['isActive'].eq(1))

        drugName = params.get('drugName', None)
        if drugName:
            cond.append(" f.id IN (SELECT master_id FROM DrugFormulary_Item LEFT JOIN rbMedicines AS d ON (d.id = drug_id) WHERE master_id = f.id AND d.name LIKE '%%%(drugName)s%%')" % {
                'drugName' : drugName
            })

        #orgStructureIndex = params.get('orgStructureIndex', None)
        #orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if orgStructureIndex else []
        #if orgStructureIdList:
        #    cond.append(tblOrgStructure['id'].inlist(orgStructureIdList))

        cols = [tblDrugFormulary['id'],
                tblDrugFormulary['type'],
                tblDrugFormulary['orgStructure_id'],
                tblDrugFormulary['begDate'],
                tblDrugFormulary['endDate'],
                tblDrugFormulary['isActive']]

        stmt = db.selectStmt(queryTable, cols, db.joinAnd(cond))
        query = db.query(stmt)
        while query.next():
            record = query.record()
            self._items.append(record)

        self._items = db.getRecordList(queryTable, cols, db.joinAnd(cond))
        self.reset()

#
# ##############################################################################
#

class CFormularyItemsModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CFormularyItemInDocTableCol(u'Наименование', 'drug_id', 400, order='name ASC')).setValueType(QVariant.Int)
        self.addCol(CInDocTableCol(u'Запас', 'limit', 100)).setValueType(QVariant.Double)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def addNewItem(self):
        self._items.append(self.getEmptyRecord())
        self.reset()

    def deleteItem(self, row):
        self._items.__delitem__(row)
        self.reset()

    def loadItems(self, formularyId, params):
        self._items = []
        if formularyId is None:
            self.reset()
            return

        db = QtGui.qApp.db

        stmt = u'''
            SELECT *
            FROM DrugFormulary_Item AS fi
            LEFT JOIN rbMedicines AS m ON m.id = fi.drug_id
            WHERE master_id = %(masterId)s
            ORDER BY m.name ASC
        ''' % {  'masterId' : formularyId }
        query = db.query(stmt)
        while query.next():
            record = query.record()
            self._items.append(record)
        self.reset()

    def saveItems(self, formularyId):
        if formularyId is None:
            return False

        db = QtGui.qApp.db

        db.transaction()

        try:
            for item in self._items:
                stmt = '''
                    INSERT INTO DrugFormulary_Item (id, master_id, drug_id, `limit`)
                    VALUES (%(id)s, %(master_id)s, %(drug_id)s, '%(limit)s')
                    ON DUPLICATE KEY UPDATE drug_id = %(drug_id)s, `limit` = '%(limit)s'
                ''' % {
                    'id' : forceInt(item.value('id')),
                    'master_id' : forceInt(formularyId),
                    'drug_id' : forceInt(item.value('drug_id')),
                    'limit' : forceDouble(item.value('limit'))
                }

                db.query(stmt)

            db.commit()
            return True
        except:
            db.rollback()
            return False

class CFormularyListModel(QtCore.QAbstractListModel):
    def __init__(self, parent):
        QtCore.QAbstractListModel.__init__(self, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if 0 <= row < len(self._items) and role == QtCore.Qt.DisplayRole:
            return self._items[row]
        return QtCore.QVariant()

class CFormularyMNNsModel(CFormularyListModel):
    def __init__(self, parent):
        CFormularyListModel.__init__(self, parent)

    def loadData(self, formularyId):
        self._items = []
        if formularyId is None:
            self.reset()
            return

        db = QtGui.qApp.db

        stmt = u'''
            SELECT d.name
            FROM DrugFormulary_Item AS f
            LEFT JOIN rbMedicines AS d ON (d.id = f.drug_id)
            WHERE master_id = %(masterId)s
        ''' % {  'masterId' : formularyId }
        query = db.query(stmt)
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            nameParts = name.split(',')
            self._items.append(nameParts[0])
        self.reset()

class CFormularyFormsModel(CFormularyListModel):
    def __init__(self, parent):
        CFormularyListModel.__init__(self, parent)

    def loadData(self, formularyId, mnn):
        self._items = []
        if formularyId is None or mnn is None:
            self.reset()
            return

        db = QtGui.qApp.db

        stmt = u'''
            SELECT d.name
            FROM DrugFormulary_Item AS f
            LEFT JOIN rbMedicines AS d ON (d.id = f.drug_id)
            WHERE master_id = %(masterId)s AND d.name LIKE '%(mnn)s%%'
        ''' % {  'masterId' : formularyId, 'mnn' : mnn }
        query = db.query(stmt)
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            nameParts = name.split(',')
            self._items.append(nameParts[1])
        self.reset()

class CFormularyFullNamesModel(CFormularyListModel):
    def __init__(self, parent):
        CFormularyListModel.__init__(self, parent)

    def loadData(self, formularyId, mnn, form):
        self._items = []
        if formularyId is None or mnn is None or form is None:
            self.reset()
            return

        db = QtGui.qApp.db

        stmt = u'''
            SELECT d.name
            FROM DrugFormulary_Item AS f
            LEFT JOIN rbMedicines AS d ON (d.id = f.drug_id)
            WHERE master_id = %(masterId)s AND d.name LIKE '%(mnn)s, %(form)s%%'
        ''' % {  'masterId' : formularyId, 'mnn' : mnn, 'form' : form }
        query = db.query(stmt)
        while query.next():
            record = query.record()
            self._items.append(forceString(record.value('name')))
        self.reset()