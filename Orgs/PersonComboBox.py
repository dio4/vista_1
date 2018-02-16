# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtGui

from library.crbcombobox import CRBComboBox
from Utils import getOrgStructureDescendants

class CPersonComboBox(CRBComboBox):
    def __init__(self, parent):
        CRBComboBox.__init__(self, parent)
        self._tableName = 'vrbPersonWithSpeciality'
        self._addNone = True
        self._orgId = QtGui.qApp.currentOrgId()
        self._orgStructureId = None
        self._orgStructureIdList = None
        self._specialityId = None
        self._specialityPresent = True
        self._postId  = None
        self._begDate = None
        self._endDate = None
        self._customFilter = None
        self._isInvestigator = None
        self.setOrderByName()
        CRBComboBox.setTable(self, self._tableName, self._addNone, self.compileFilter(), self._order)


    def setTable(self, tableName, addNone=True, filter='', order=None):
        assert False
#        self._customFilter = filter
#        self._tableName = tableName
#        CRBComboBox.setTable(self, tableName, addNone, self.compileFilter(), order or self._order)

#                self.cmbPerson.setTable('vrbPersonWithSpeciality', False, filter='org_id = \'%s\'' % QtGui.qApp.currentOrgId(), order='name, code')
#    setTable('vrbPersonWithSpeciality', False, filter='org_id = \'%s\'' % QtGui.qApp.currentOrgId(), order='name, code')


    def setAddNone(self, addNone=True):
        if self._addNone != addNone:
            self._addNone = addNone
            self.updateFilter()


    def setOrgId(self, orgId):
        if self._orgId != orgId:
            self._orgId = orgId
            self.updateFilter()


    def setOrgStructureId(self, orgStructureId):
        if self._orgStructureId != orgStructureId:
            self._orgStructureId = orgStructureId
            if orgStructureId:
                idList = getOrgStructureDescendants(orgStructureId)
            else:
                idList = None
            if self._orgStructureIdList != idList:
                self._orgStructureIdList = idList
                self.updateFilter()


    def setSpecialityId(self, specialityId):
        if self._specialityId != specialityId:
            self._specialityId = specialityId
            self.updateFilter()


    def setSpecialityPresent(self, specialityPresent):
        if self._specialityPresent != specialityPresent:
            self._specialityPresent = specialityPresent
            self.updateFilter()


#    def setPostId(self, postId):
#        pass



    def setBegDate(self, begDate):
        if self._begDate != begDate:
            self._begDate = begDate
            self.updateFilter()


    def setEndDate(self, endDate):
        if endDate:
            date = endDate.addMonths(-1)
        else:
            date = None
        if self._endDate != date:
            self._endDate = date
            self.updateFilter()

    def setIsInvestigator(self, isInvestigator):
        if self._isInvestigator != isInvestigator:
            self._isInvestigator = isInvestigator
            self.updateFilter()


    def setFilter(self, filter):
        if self._customFilter != filter:
            self._customFilter = filter
            self.updateFilter()


    def compileFilter(self):
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        cond = []
        if self._orgId:
            cond.append( table['org_id'].eq(self._orgId))
        if self._orgStructureIdList:
            cond.append( table['orgStructure_id'].inlist(self._orgStructureIdList) )
        if self._specialityId:
            if isinstance(self._specialityId, list):
                cond.append( table['speciality_id'].inlist(self._specialityId) )
            else:
                cond.append( table['speciality_id'].eq(self._specialityId) )
        elif self._specialityPresent:
            cond.append( table['speciality_id'].isNotNull() )
        if self._postId:
            if isinstance(self._postId, list):
                cond.append( table['post_id'].inlist(self._postId) )
            else:
                cond.append( table['post_id'].eq(self._postId) )
        if self._endDate:
            cond.append(db.joinOr([table['retireDate'].isNull(), table['retireDate'].ge(self._endDate)]))
        if self._customFilter:
            cond.append(self._customFilter)
        return db.joinAnd(cond)


    def updateFilter(self):
        v = self.value()
        CRBComboBox.setTable(self, self._tableName, self._addNone, self.compileFilter(), self._order)
        self.setValue(v)


    def setOrderByCode(self):
        self._order = 'code, name'


    def setOrderByName(self):
        self._order = 'name, code'

    def setOrder(self, order):
        self._order = order
