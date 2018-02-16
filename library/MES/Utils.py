#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *


#def getServiceIdList(mesId, necessity=None):
#    result = []
#    db = QtGui.qApp.db
#    stmt = u'''SELECT DISTINCT rbService.id FROM rbService
#LEFT JOIN mes.mrbService  ON rbService.code = mes.mrbService.code OR rbService.code = SUBSTRING(mes.mrbService.code,2)
#LEFT JOIN mes.MES_service ON mes.MES_service.service_id = mes.mrbService.id
#WHERE mes.MES_service.master_id = %d AND rbService.id IS NOT NULL''' % mesId
#    if not necessity is None:
#        stmt += ' AND mes.MES_service.necessity = %f ' % necessity
#    query = db.query(stmt)
#    while query.next():
#        record = query.record()
#        result.append(forceRef(record.value(0)))
#    return result

def getServiceIdList(mesId, necessity=None, isGrouping = False, date = None):
    result = [] if not isGrouping else {}
    db = QtGui.qApp.db
    tblService = db.table('rbService')
    tblMrbService = db.table('mes.mrbService')
    tblMesService = db.table('mes.MES_service')

    queryTable = tblService.leftJoin(tblMrbService, tblMrbService['code'].eq(tblService['code']))
    queryTable = queryTable.leftJoin(tblMesService, tblMesService['service_id'].eq(tblMrbService['id']))

    cond = [tblMesService['master_id'].eq(mesId),
            tblMesService['deleted'].eq(0),
            tblMrbService['deleted'].eq(0),
            ]
    if not necessity is None:
        cond.append(tblMesService['necessity'].eq(necessity))
    if not date is None:
        dateStr = date.toString(QtCore.Qt.ISODate)
        cond.append('IF(mes.MES_service.begDate IS NULL, 1, mes.MES_service.begDate <= DATE(\'%s\'))' % dateStr)
        cond.append('IF(mes.MES_service.endDate IS NULL, 1, mes.MES_service.endDate >= DATE(\'%s\'))' % dateStr)
    cols = [tblService['id'], tblMesService['groupCode']]

    recordList = db.getRecordList(queryTable, cols, cond, isDistinct=True)
    for record in recordList:
        serviceId = forceRef(record.value(0))
        
        if isGrouping:
            serviceGroupCode = forceRef(record.value(1))
            result.setdefault(serviceGroupCode, []).append(serviceId)
        else:
            result.append(serviceId)
    return result


def getMedicamentServiceIdList(mesId, necessity=None):
    result = []
    db = QtGui.qApp.db
    stmt = u'''SELECT DISTINCT
    rbService.id
FROM
    rbService
        LEFT JOIN
    mes.mrbMedicament ON rbService.code = mes.mrbMedicament.code
        LEFT JOIN
    mes.MES_medicament ON mes.MES_medicament.medicamentCode = mes.mrbMedicament.code
WHERE
    mes.MES_medicament.master_id = %d
        AND mes.MES_medicament.deleted = 0
        AND mes.mrbMedicament.deleted = 0
        AND rbService.id IS NOT NULL''' % mesId
    if not necessity is None:
        stmt += ' AND mes.MES_medicament.necessity = %f' % necessity
    query = db.query(stmt)
    while query.next():
        record = query.record()
        result.append(forceRef(record.value(0)))
    return result


# Not used.
def getActionTypeIdList(mesId, necessity=None, date = None):
    serviceIdList = getServiceIdList(mesId, necessity, date = date)
    db = QtGui.qApp.db
    tableActionTypeService = db.table('ActionType_Service')
    tableActionType = db.table('ActionType')
    cond = [tableActionType['deleted'].eq(0),
            tableActionTypeService['service_id'].inlist(serviceIdList)
           ]
    table = tableActionTypeService.leftJoin(tableActionType, tableActionType['id'].eq(tableActionTypeService['master_id']))
    result = db.getDistinctIdList(table, tableActionTypeService['master_id'].name(), cond)
    return result


def getMesServiceInfo(serviceCode, mesId, necessity = None):
    # Нужна ли проверка дат?
    db = QtGui.qApp.db
    mesCondition = 'mes.MES_service.master_id %s' % ('IS NULL' if mesId is None else ' = %d' % mesId)
    necessityCond = ' AND mes.MES_service.necessity = %.2f' % necessity if necessity else ''
    stmt = u'''
            SELECT 
                mes.mrbService.doctorWTU,
                mes.mrbService.paramedicalWTU,
                mes.MES_service.averageQnt as averageQnt,
                mes.MES_service.necessity
            FROM
                mes.MES_service
                    LEFT JOIN
                mes.mrbService ON mes.mrbService.id = mes.MES_service.service_id
            WHERE
                %s 
                AND mes.mrbService.code = '%s'
                AND mes.MES_service.deleted = 0
                AND mes.mrbService.deleted = 0
                
    ''' % (mesCondition + necessityCond, serviceCode)
    query = db.query(stmt)
    if query.first():
        return query.record()
    mesCondition = 'mes.MES_medicament.master_id %s' % ('IS NULL' if mesId is None else ' = %d' % mesId)
    necessityCond = ' AND mes.MES_medicament.necessity = %.2f' % necessity if necessity else ''
    stmt = u'''
            SELECT 
                0,
                0,
                mes.MES_medicament.averageQnt as averageQnt,
                mes.MES_medicament.necessity
            FROM
                mes.MES_medicament
            WHERE
                %s
                    AND mes.MES_medicament.medicamentCode = '%s'
                    AND mes.MES_medicament.deleted = 0
            
            ''' % (mesCondition + necessityCond, serviceCode)
    query = db.query(stmt)
    if query.first():
        return query.record()

    return None


def getCmbMesType(event):
    """
    return:
    0 if not MES or CSG or EventEditPage hasn't tabMes or tabMes hasn't cmbMes
    1 if MES,
    2 if CSG,
    """
    from library.MES.MESComboBox import CMESComboBox
    from library.CSG.CSGComboBox import CCSGComboBox
    if not hasattr(event, 'tabMes'): return 0
    if not hasattr(event.tabMes, 'cmbMes'): return 0
    if type(event.tabMes.cmbMes) == CCSGComboBox: return 2
    if type(event.tabMes.cmbMes) == CMESComboBox: return 1
    return 0
