#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.AgeSelector import parseAgeSelector, checkExtendedAgeSelector
from library.Utils import forceString, forceInt, forceRef, forceDouble


def getCSGDepartmentMaskByRegionalCode(code):
    if code == '11' or code == '12':
        return 'G10%%'
    elif code == '51' or code == '52':
        return 'G50%%'
    elif code == '71' or code == '72':
        return 'G70%%'
    elif code == '41' or code == '42' or code == '43' or code == '90':
        return 'G40%%'


# code — Подразделение стационара. Результат getCSGDepartmentMaskByRegionalCode
def getCsgIdListByCond(
        sex=None,
        age=None,
        mkb=None,
        mkb2List=[],
        actionTypeCodesList=[],
        code=None,
        date=QtCore.QDate.currentDate(),
        duration=None,
        weakSelection=False
):
    db = QtGui.qApp.db
    tblSPR69 = db.table('mes.SPR69')
    tblSPR70 = db.table('mes.SPR70')

    def checkDuration(durationTag, duration):
        if duration is None: return True
        return (durationTag == 0 and duration >= 3) or (durationTag == 1 and duration < 3)

    def checkAge(ageTag, age):
        if age is None: return True
        ageSelectors = parseAgeSelector(ageTag, isExtend=True)
        return checkExtendedAgeSelector(ageSelectors, age)

    def filterSPR69Records(recordList):
        isMKBX = False
        isMKBX2 = False
        isKUSL = False
        isSEX = False
        isAGE = False
        isDuration = False

        for r in recordList:
            isMKBX = isMKBX or (
                bool(forceString(r.value('MKBX'))) and forceString(r.value('MKBX')) == mkb
            )
            isMKBX2 = isMKBX2 or (bool(forceString(r.value('MKBX2'))) and forceString(r.value('MKBX2')) in mkb2List)
            isKUSL = isKUSL or (
                bool(forceString(r.value('KUSL'))) and forceString(r.value('KUSL')) in actionTypeCodesList
            )
            isSEX = isSEX or (bool(forceInt(r.value('sex'))) and forceInt(r.value('sex')) == sex)
            isAGE = isAGE or (
                (forceString(r.value('age')) != u'0д-125г') and checkAge(forceString(r.value('age')), age)
            )  # TODO:skkachaev:Attention!!! Завязываемся на то, как мы делаем импорт!!! ImportSPR69
            isDuration = isDuration or (
                checkDuration(forceInt(r.value('duration')), duration) and (forceInt(r.value('duration')) == 1)
            )

        result = dict()

        for r in recordList:
            #i4605 Марина попросила именно откатить, а не исправлять
            if duration is not None and duration > 3 and forceInt(r.value('duration')) == 1:
                continue
            # if duration is not None:
            #     if duration > 3 and forceInt(r.value('duration')) == 1:
            #         continue
            #     if duration <= 3 and forceInt(r.value('duration')) == 0:
            #         continue

            cond = True
            cond = cond and (bool(forceString(r.value('MKBX'))) if isMKBX else True)
            cond = cond and (bool(forceString(r.value('MKBX2'))) if isMKBX2 else True)
            cond = cond and (bool(forceString(r.value('KUSL'))) if isKUSL else True)
            cond = cond and (bool(forceInt(r.value('sex'))) if isSEX else True)
            cond = cond and (bool(forceString(r.value('age')) != u'0д-125г') if isAGE else True)
            cond = cond and (bool(forceInt(r.value('duration')) == 1) if isDuration else True)

            if cond:
                if forceString(r.value('KSG')) not in result:
                    result[forceString(r.value('KSG'))] = r
                # if  (bool(forceString(r.value('MKBX'))) if isMKBX else True) and \
                #     (bool(forceString(r.value('MKBX2'))) if isMKBX2 else True) and \
                #     (bool(forceString(r.value('KUSL'))) if isKUSL else True) and \
                #     (bool(forceInt(r.value('sex'))) if isSEX else True) and \
                #     ((forceString(r.value('age')) != u'0д-125г') if isAGE else True) and \
                #     ((forceInt(r.value('duration')) == 1) if isDuration else True):
                #     result.append(r)

        return result.values()

    def filterSPr69RecordsByAge(recordList):
        flag = False
        for record in recordList:
            rage = forceString(record.value('age'))
            if rage == u'-27д' or rage == u'28д-90д' or rage == u'91д-366д': flag = True

        result = []
        for record in recordList:
            if (forceString(record.value('age')) == u'0г-17г') and flag:
                pass
            elif checkAge(forceString(record.value('age')), age):
                result.append(record)

        return result

    # return [mes.SPR69.record]
    def getCsgListByDiagnosis():
        if not mkb: return []

        cond = [u''' '%s' LIKE `mes`.`SPR69`.MKBX''' % mkb]
        if date: cond.append(
            u''' '%s' BETWEEN `mes`.`SPR69`.begDate AND `mes`.`SPR69`.endDate''' % date.toString('yyyy-MM-dd'))
        if sex: cond.append(db.joinOr([tblSPR69['sex'].eq(0), tblSPR69['sex'].eq(sex)]))
        if code: cond.append(tblSPR69['KSG'].like(code))
        if duration and duration < 3: cond.append(db.joinOr([tblSPR69['duration'].eq(1), tblSPR69['duration'].eq(0)]))
        if mkb2List != ['']:
            mkb2Cond = [tblSPR69['MKBX2'].eq('')]
            for mkb2 in mkb2List: mkb2Cond.append(u''' '%s' LIKE `mes`.`SPR69`.MKBX2''' % mkb2)
            cond.extend([db.joinOr(mkb2Cond)])
        if len(actionTypeCodesList) != 0:
            uslCond = [tblSPR69['KUSL'].eq('')]
            for usl in actionTypeCodesList: uslCond.append(u''' '%s' LIKE `mes`.`SPR69`.KUSL''' % usl)
            cond.extend([db.joinOr(uslCond)])

        csgList = db.getRecordList(table=tblSPR69,
                                   cols='*',
                                   isDistinct=True,
                                   where=db.joinAnd(cond))

        result = []
        for csg in csgList:
            ageString = forceString(csg.value('age'))

            skipCsg = False
            for x in result:
                if csg.value('KSG') == x.value('KSG'):
                    skipCsg = True
                    break

            # Проверяем на наличие в списке таким образом, потому что исходный
            # вариант сравнивал адреса csg и элемента списка result. Адреса будут
            # в большинстве случаев разные, а вот содержимое может совпадать
            if not skipCsg:  # csg not in result:
                if age is None:
                    result.append(csg)
                    continue
                if ageString:
                    ageSelectors = parseAgeSelector(ageString, isExtend=True)
                    if checkExtendedAgeSelector(ageSelectors, age):
                        result.append(csg)
                        # break

        result = filterSPr69RecordsByAge(filterSPR69Records(result))
        return result

    # return [mes.SPR69.record]
    def getCsgListByServices():
        if not actionTypeCodesList: return []

        cond = [db.joinOr([u''' '%s' LIKE `mes`.`SPR69`.KUSL''' % usl for usl in actionTypeCodesList])]
        if date: cond.append(
            u''' '%s' BETWEEN `mes`.`SPR69`.begDate AND `mes`.`SPR69`.endDate''' % date.toString('yyyy-MM-dd'))
        if sex: cond.append(db.joinOr([tblSPR69['sex'].eq(0), tblSPR69['sex'].eq(sex)]))
        if code: cond.append(tblSPR69['KSG'].like(code))
        if duration and duration < 3: cond.append(db.joinOr([tblSPR69['duration'].eq(1), tblSPR69['duration'].eq(0)]))
        if mkb: cond.append(db.joinOr([tblSPR69['MKBX'].eq(''),
                                       u''' '%s' LIKE `mes`.`SPR69`.MKBX''' % mkb]))
        # if mkb2List != ['']:
        if mkb2List:
            mkb2Cond = [tblSPR69['MKBX2'].eq('')]
            for mkb2 in mkb2List: mkb2Cond.append(u''' '%s' LIKE `mes`.`SPR69`.MKBX2''' % mkb2)
            cond.extend([db.joinOr(mkb2Cond)])

        csgList = db.getRecordList(table=tblSPR69,
                                   cols='*',
                                   isDistinct=True,
                                   where=db.joinAnd(cond))

        result = []
        for csg in csgList:
            ageString = forceString(csg.value('age'))

            skipCsg = False
            for x in result:
                if csg.value('KSG') == x.value('KSG'):
                    skipCsg = True
                    break
            # TODO: pirozhok
            # Проверяем на наличие в списке таким образом, потому что исходный
            # вариант сравнивал адреса csg и элемента списка result. Адреса будут
            # в большинстве случаев разные, а вот содержимое может совпадать.
            if not skipCsg:  # csg not in result:
                if age is None:
                    result.append(csg)
                    continue
                if ageString:
                    ageSelectors = parseAgeSelector(ageString, isExtend=True)
                    if checkExtendedAgeSelector(ageSelectors, age):
                        result.append(csg)

        result = filterSPr69RecordsByAge(filterSPR69Records(result))
        return result

    # noinspection PySetFunctionToLiteral
    def checkIf220():
        # G10.2917.220
        gt1 = set(('S02.0', 'S02.1', 'S04.0', 'S05.7', 'S06.1', 'S06.2', 'S06.3', 'S06.4', 'S06.5', 'S06.6', 'S06.7',
                   'S07.0', 'S07.1', 'S07.8', 'S09.0', 'S11.0', 'S11.1', 'S11.2', 'S11.7', 'S15.0', 'S15.1', 'S15.2',
                   'S15.3', 'S15.7', 'S15.8', 'S15.9', 'S17.0', 'S17.8', 'S18'))
        gt2 = set(('S12.0', 'S12.9', 'S13.0', 'S13.1', 'S13.3', 'S14.0', 'S14.3', 'S22.0', 'S23.0', 'S23.1', 'S24.0',
                   'S32.0', 'S32.1', 'S33.0', 'S33.1', 'S33.2', 'S33.4', 'S34.0', 'S34.3', 'S34.4'))
        gt3 = set(('S22.2', 'S22.4', 'S22.5', 'S25.0', 'S25.1', 'S25.2', 'S25.3', 'S25.4', 'S25.5', 'S25.7', 'S25.8',
                   'S25.9', 'S26.0', 'S27.0', 'S27.1', 'S27.2', 'S27.4', 'S27.5', 'S27.6', 'S27.8', 'S28.0', 'S28.1'))
        gt4 = set(('S35.0', 'S35.1', 'S35.2', 'S35.3', 'S35.4', 'S35.5', 'S35.7', 'S35.8', 'S35.9', 'S36.0', 'S36.1',
                   'S36.2', 'S36.3', 'S36.4', 'S36.5', 'S36.8', 'S36.9', 'S37.0', 'S38.3'))
        gt5 = set(('S32.3', 'S32.4', 'S32.5', 'S36.6', 'S37.1', 'S37.2', 'S37.4', 'S37.5', 'S37.6', 'S37.8', 'S38.0',
                   'S38.2'))
        gt6 = set(('S42.2', 'S42.3', 'S42.4', 'S42.8', 'S45.0', 'S45.1', 'S45.2', 'S45.7', 'S45.8', 'S47', 'S48.0',
                   'S48.1', 'S48.9', 'S52.7', 'S55.0', 'S55.1', 'S55.7', 'S55.8', 'S57.0', 'S57.8', 'S57.9', 'S58.0',
                   'S58.1', 'S58.9', 'S68.4', 'S71.7', 'S72.0', 'S72.1', 'S72.2', 'S72.3', 'S72.4', 'S72.7', 'S75.0',
                   'S75.1', 'S75.2', 'S75.7', 'S75.8', 'S77.0', 'S77.1', 'S77.2', 'S78.0', 'S78.1', 'S78.9', 'S79.7',
                   'S82.1', 'S82.2', 'S82.3', 'S82.7', 'S85.0', 'S85.1', 'S85.5', 'S85.7', 'S87.0', 'S87.8', 'S88.0',
                   'S88.1', 'S88.9', 'S95.7', 'S95.8', 'S95.9', 'S97.0', 'S97.8', 'S98.0'))
        gt7 = set(('S02.7', 'S12.7', 'S22.1', 'S27.7', 'S29.7', 'S31.7', 'S32.7', 'S36.7', 'S38.1', 'S39.6', 'S39.7',
                   'S37.7', 'S42.7', 'S49.7', 'T01.1', 'T01.8', 'T01.9', 'T02.0', 'T02.1', 'T02.2', 'T02.3', 'T02.4',
                   'T02.5', 'T02.6', 'T02.7', 'T02.8', 'T02.9', 'T04.0', 'T04.1', 'T04.2', 'T04.3', 'T04.4', 'T04.7',
                   'T04.8', 'T04.9', 'T05.0', 'T05.1', 'T05.2', 'T05.3', 'T05.4', 'T05.5', 'T05.6', 'T05.8', 'T05.9',
                   'T06.0', 'T06.1', 'T06.2', 'T06.3', 'T06.4', 'T06.5', 'T06.8', 'T07'))
        gt = set(('J94.2', 'J94.8', 'J94.9', 'J93', 'J93.0', 'J93.1', 'J93.8', 'J93.9', 'J96.0', 'N17', 'T79.4',
                  'R57.1', 'R57.8'))
        mkbs = set(mkb2List + [mkb])
        # Если среди MKB есть любой из группы T, а также один из T7 или два из разных групп T1-T6
        return gt & mkbs and (gt7 & mkbs or sum(bool(g & mkbs) for g in (gt1, gt2, gt3, gt4, gt5, gt6)) >= 2)

    diagCSGList = getCsgListByDiagnosis()
    serviceCSGList = getCsgListByServices()

    id220 = db.getIdList(
        stmt="SELECT id FROM mes.SPR69 WHERE KSG = 'G10.2917.220' AND NOW() BETWEEN begDate AND endDate"
    ) if checkIf220() else []

    # Если получилось несколько, то что-то пошло не правильно, но врачи в комбобоксе смогут выбрать правильно.
    # Если в одной ветке не получилось — вываливаем другую
    if len(diagCSGList) == 0: return [forceRef(csg.value('id')) for csg in serviceCSGList] + id220
    if len(serviceCSGList) == 0: return [forceRef(csg.value('id')) for csg in diagCSGList] + id220
    if len(diagCSGList) > 1 or len(serviceCSGList) > 1: return list(
        set([forceRef(csg.value('id')) for csg in diagCSGList] +
            [forceRef(csg.value('id')) for csg in serviceCSGList] +
            id220))

    tryCombinationCSG = db.getColumnValues(
        table=tblSPR70,
        column='KSGITOG',
        where=[
            tblSPR70['KSGMKBX'].eq(forceString(diagCSGList[0].value('KSG'))),
            tblSPR70['KSGKUSL'].eq(forceString(serviceCSGList[0].value('KSG')))
        ],
        limit=1
    )

    if tryCombinationCSG:
        if tryCombinationCSG[0] == diagCSGList[0].value('KSG'):
            return [forceRef(diagCSGList[0].value('id'))] + id220
        else:
            return [forceRef(serviceCSGList[0].value('id'))] + id220

    if weakSelection:
        res = diagCSGList
        for x in serviceCSGList:
            skipCsg = False
            for y in res:
                if forceString(x.value('KSG')) == forceString(y.value('KSG')):
                    skipCsg = True
                    break
            if not skipCsg:
                res.append(x)

        return [forceRef(csg.value('id')) for csg in res] + id220

    diagCSGKoeff = forceDouble(diagCSGList[0].value('KSGKoeff'))
    serviceCSGKoeff = forceDouble(serviceCSGList[0].value('KSGKoeff'))
    if diagCSGKoeff > serviceCSGKoeff:
        return [forceRef(diagCSGList[0].value('id'))] + id220
    else:
        return [forceRef(serviceCSGList[0].value('id'))] + id220
