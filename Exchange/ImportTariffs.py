# -*- coding: utf-8 -*-
from Cimport import *
from Ui_ImportTariffs import Ui_Dialog


def ImportTariffs(widget, contractId, begDate, endDate, tariffList):
    try:
        setEIS_db()
        dlg=CImportTariffs(widget, QtGui.qApp.EIS_db, contractId, begDate, endDate, tariffList)
        dlg.exec_()
        return dlg.ok, dlg.tariffList
    except:
        EIS_close()
        return False, []


class CImportTariffs(CEISimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent, EIS_db, contractId, begDate, endDate, tariffList):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.parent=parent
        self.EIS_db=EIS_db
        self.contractId=contractId
        self.begDate = begDate
        self.endDate = endDate
        self.tariffList = map(None, tariffList)
        self.tariffDict = {}
        for i, tariff in enumerate(self.tariffList):
            key = ( forceInt(tariff.value('tariffType')),
                    forceRef(tariff.value('service_id')),
                    forceString(tariff.value('age')),
                    forceRef(tariff.value('unit_id')) )
            tariffIndexList = self.tariffDict.setdefault(key, [])
            tariffIndexList.append(i)
        self.tblContract_Tariff=tbl('Contract_Tariff')
        self.tblContract=tbl('Contract')
        self.ok = False
        self._mapAmountAndINFIS_CODE2Exists = {}


    def startImport(self):
        self._mapAmountAndINFIS_CODE2Exists.clear()
        self.ok = False
        db=QtGui.qApp.db
        EIS_db=self.EIS_db
        if not EIS_db:
            return
        loadChildren=self.chkLoadChildren.isChecked()
        loadAdult=self.chkLoadAdult.isChecked()
        if not (loadChildren or loadAdult):
            self.log.append(u'Нечего загружать')
            return
        amb=self.chkAmb.isChecked()
        stom=self.chkStom.isChecked()
        completeCase = self.chkCompleteCase.isChecked()
        dailyStat = self.chkDailyStat.isChecked()
        operV = self.chkOperV.isChecked()
        ID_PROFILE_TYPEList=[]
        if amb:
            ID_PROFILE_TYPEList.append(3)
        if stom:
            ID_PROFILE_TYPEList.append(4)
        if completeCase:
            ID_PROFILE_TYPEList.append(7)
        if dailyStat:
            ID_PROFILE_TYPEList.append(8)
        if operV:
            ID_PROFILE_TYPEList.append(9)
        if not ID_PROFILE_TYPEList:
            self.log.append(u'Нечего загружать')
            return
        n=0
#        prof_found=0
#        prof_add=0

        begDateStr='\''+unicode(self.begDate.toString('dd.MM.yyyy'))+'\''
        endDateStr='\''+unicode(self.endDate.toString('dd.MM.yyyy'))+'\''
        zone=''
        if loadChildren and not loadAdult:
            zone=' AND VMU_TARIFF.ID_ZONE_TYPE=3 '
        if loadAdult and not loadChildren:
            zone=' AND VMU_TARIFF.ID_ZONE_TYPE=1 '
        # КАВЫЧКИ В ИНТЕРБЕЙСЕ (В DIALECT 3) ИСПОЛЬЗУЮТСЯ ДЛЯ ЭКРАНИРОВАНИЯ ИМЁН ПОЛЕЙ!
        stmt = u'''
        SELECT %s
        FROM VMU_TARIFF
        JOIN VMU_PROFILE ON VMU_PROFILE.ID_PROFILE=VMU_TARIFF.ID_PROFILE
        WHERE VMU_TARIFF.TARIFF_END_DATE = (
            SELECT t2.TARIFF_END_DATE
            FROM VMU_TARIFF t2
            WHERE t2.ID_TARIFF = (
                SELECT MAX(ID_TARIFF)
                FROM VMU_TARIFF t3
                WHERE t3.ID_PROFILE=VMU_TARIFF.ID_PROFILE
                    AND t3.ID_ZONE_TYPE=VMU_TARIFF.ID_ZONE_TYPE
                    AND t3.TARIFF_BEGIN_DATE <= ''' + endDateStr + u'''
            )
        )
        AND VMU_TARIFF.TARIFF_BEGIN_DATE = (
            SELECT t4.TARIFF_BEGIN_DATE
            FROM VMU_TARIFF t4
            WHERE t4.ID_TARIFF = (
                SELECT MAX(ID_TARIFF)
                FROM VMU_TARIFF t5
                WHERE t5.ID_PROFILE=VMU_TARIFF.ID_PROFILE
                    AND t5.ID_ZONE_TYPE = VMU_TARIFF.ID_ZONE_TYPE
            )
        )
        AND VMU_PROFILE.ID_PROFILE_TYPE IN ('''+', '.join(str(x) for x in ID_PROFILE_TYPEList)+u''')
        AND VMU_PROFILE.PROFILE_END_DATE>=''' + begDateStr + u'''
        AND VMU_PROFILE.PROFILE_BEGIN_DATE<=''' + endDateStr+zone
        tmpStmt = stmt
        stmt = stmt % '*'
        print stmt
        query = EIS_db.query(stmt + 'ORDER BY PROFILE_INFIS_CODE, AMOUNT DESC')
        query.setForwardOnly(True)
        num=query.size() # Этот фокус не катит в случае interbase
        self.progressBar.setMaximum(max(num, 0))
        updatedTariffs = {}
        n_add=0
        n_edit=0
        self.previousPROFILE_INFIS_CODE = None
        self.previousID_ZONE_TYPE       = None
        self.tariffListAdult = []
        self.tariffListChild = []
        while query.next():
            QtGui.qApp.processEvents()
            if self.abort:
                break
            record = query.record()
            PROFILE_INFIS_CODE=forceString(record.value('PROFILE_INFIS_CODE'))
            PROFILE_BEGIN_DATE=record.value('PROFILE_BEGIN_DATE')
            PROFILE_END_DATE=record.value('PROFILE_END_DATE')
            ID_ZONE_TYPE=forceInt(record.value('ID_ZONE_TYPE'))
            ID_PROFILE_TYPE=forceInt(record.value('ID_PROFILE_TYPE'))
            tbd = unicode(forceDate(record.value('TARIFF_BEGIN_DATE')).toString('yyyy.MM.dd'))
            if self.previousPROFILE_INFIS_CODE == PROFILE_INFIS_CODE and self.previousID_ZONE_TYPE == ID_ZONE_TYPE:
                continue
            self.previousPROFILE_INFIS_CODE = PROFILE_INFIS_CODE
            self.previousID_ZONE_TYPE = ID_ZONE_TYPE
            n+=1
            if num<=0:
                self.labelNum.setText(u'Всего записей в источнике: '+str(n))
            self.n=n
            age=u''
            if ID_ZONE_TYPE==1:
                age=u'18г-'
            if ID_ZONE_TYPE==3:
                age=u'-17г'
            service_id=forceInt(db.translate('rbService', 'infis', PROFILE_INFIS_CODE, 'id'))
            if not service_id:
                self.err2log(PROFILE_INFIS_CODE, u'Услуга не найдена')
                continue
            price = forceDouble(record.value('PRICE'))

            tariffType = 0
            unit_id = 1
            uet = 0.0
            amount = 1.0
            if ID_PROFILE_TYPE == 4:
                tariffType = 5
                unit_id = 3
                uet = forceDouble(record.value('UET'))
                if stom:
                    amount = 0.0
            if ID_PROFILE_TYPE == 7:
                tariffType = 8
                unit_id = 4
            if ID_PROFILE_TYPE == 8:
                tariffType = 10
                unit_id = 4
                amount = forceDouble(record.value('AMOUNT'))
                if not amount:
                    amount = 1.0
                price = price/amount
            if ID_PROFILE_TYPE == 9:
                tariffType = 2
                unit_id = 7
            key = ( tariffType, service_id, age, unit_id )
            tariffIndexList = self.tariffDict.get(key, None)
            if tariffIndexList is not None:
                localEdit = False
                for i in tariffIndexList:
                    tariff = self.tariffList[i]
                    updatedTariffs[i] = (tbd, amount)
                    oldPrice=forceDouble(tariff.value('price'))
                    oldUet = forceDouble(tariff.value('uet'))
                    oldAmount = forceDouble(tariff.value('amount'))
                    if ID_PROFILE_TYPE == 7:
                        result = self.calculateTariffData(record, tmpStmt)
                        if result:
                            result = self.format7Values(*result)
                            amount, price, f1Start, f1Sum, f1Price, f2Start, f2Sum, f2Price = result
                            
                            oldF1Start = forceDouble(tariff.value('frag1Start'))
                            oldF1Sum   = forceDouble(tariff.value('frag1Sum'))
                            oldF1Price = forceDouble(tariff.value('frag1Price'))
                            
                            oldF2Start = forceDouble(tariff.value('frag2Start'))
                            oldF2Sum   = forceDouble(tariff.value('frag2Sum'))
                            oldF2Price = forceDouble(tariff.value('frag2Price'))
                            
                            if abs(f1Start-oldF1Start) > 0.001:
                                localEdit = True
                                tariff.setValue('frag1Start', toVariant(f1Start))
                                self.err2log(PROFILE_INFIS_CODE, 
                                             u'Начало Ф1 изменено '+str(oldF1Start)+u' на '+str(f1Start))
                                             
                            if abs(f1Sum-oldF1Sum) > 0.001:
                                localEdit = True
                                tariff.setValue('frag1Sum', toVariant(f1Sum))
                                self.err2log(PROFILE_INFIS_CODE, 
                                             u'Начальная сумма Ф1 '+str(oldF1Sum)+u' на '+str(f1Sum))
                                             
                            if abs(f1Price-oldF1Price) > 0.001:
                                localEdit = True
                                tariff.setValue('frag1Price', toVariant(f1Price))
                                self.err2log(PROFILE_INFIS_CODE, 
                                             u'Цена в Ф1 изменена '+str(oldF1Price)+u' на '+str(f1Price))
                                             
                                             
                                             
                            if abs(f2Start-oldF2Start) > 0.001:
                                localEdit = True
                                tariff.setValue('frag2Start', toVariant(f2Start))
                                self.err2log(PROFILE_INFIS_CODE, 
                                             u'Начало Ф2 изменено '+str(oldF2Start)+u' на '+str(f2Start))
                                             
                            if abs(f2Sum-oldF2Sum) > 0.001:
                                localEdit = True
                                tariff.setValue('frag2Sum', toVariant(f2Sum))
                                self.err2log(PROFILE_INFIS_CODE, 
                                             u'Начальная сумма Ф2 '+str(oldF2Sum)+u' на '+str(f2Sum))
                                             
                            if abs(f2Price-oldF2Price) > 0.001:
                                localEdit = True
                                tariff.setValue('frag2Price', toVariant(f2Price))
                                self.err2log(PROFILE_INFIS_CODE, 
                                             u'Цена в Ф1 изменена '+str(oldF2Price)+u' на '+str(f2Price))
                        else:
                            continue
                         
                    if abs(price-oldPrice)>0.001:
                        localEdit = True
                        tariff.setValue('price', toVariant(price))
                        self.err2log(PROFILE_INFIS_CODE, u'Цена изменена с '+str(oldPrice)+u' на '+str(price))
                    if abs(uet-oldUet)>0.001:
                        localEdit = True
                        tariff.setValue('uet', toVariant(uet))
                        self.err2log(PROFILE_INFIS_CODE, u'УЕТ изменён с '+str(oldUet)+u' на '+str(uet))
                    if abs(amount-oldAmount)>0.001:
                        localEdit = True
                        tariff.setValue('amount', toVariant(amount))
                        self.err2log(PROFILE_INFIS_CODE, u'Количество изменено с '+str(oldAmount)+u' на '+str(amount))
                            
                    if localEdit:
                        n_edit+=1
                    else:
                        self.err2log(PROFILE_INFIS_CODE, u'Не изменён')
            else:
                tariff=self.tblContract_Tariff.newRecord()
                
                tariff.setValue('master_id', toVariant(self.contractId))
                tariff.setValue('tariffType', toVariant(tariffType))
                tariff.setValue('service_id', toVariant(service_id))
                tariff.setValue('age', toVariant(age))
                tariff.setValue('unit_id', toVariant(unit_id))
                tariff.setValue('uet', toVariant(uet))
                if ID_PROFILE_TYPE == 7:
                    result = self.calculateTariffData(record, tmpStmt)
                    if result:
                        result = self.format7Values(*result)
                        amount, price, f1Start, f1Sum, f1Price, f2Start, f2Sum, f2Price = result
                        eventType_id = self.toKnowEventTypeId(record)
                        
                        tariff.setValue('frag1Start', toVariant(f1Start))
                        tariff.setValue('frag1Sum', toVariant(f1Sum))
                        tariff.setValue('frag1Price', toVariant(f1Price))
                        tariff.setValue('frag2Start', toVariant(f2Start))
                        tariff.setValue('frag2Sum', toVariant(f2Sum))
                        tariff.setValue('frag2Price', toVariant(f2Price))
                        tariff.setValue('eventType_id', toVariant(eventType_id))
                        
                    else:
                        continue
                tariff.setValue('amount', toVariant(amount))
                tariff.setValue('price', toVariant(price))
                i = len(self.tariffList)
                self.tariffDict[key] = [i]
                self.tariffList.append(tariff)
                updatedTariffs[i] = (tbd, amount)
                n_add+=1
                self.err2log(PROFILE_INFIS_CODE, u'добавлен')

        for i, tariff in enumerate(self.tariffList):
            if i in updatedTariffs:
                continue
            serviceId=forceRef(tariff.value('service_id'))
            PROFILE_INFIS_CODE=forceString(db.translate('rbService', 'id', serviceId, 'infis'))
            self.tariffList[i] = None
            self.err2log(PROFILE_INFIS_CODE, u'удалён')

        self.tariffList = filter(None, self.tariffList)

        prevContract=db.getRecordEx(
            self.tblContract,
            'MAX(begDate)',
            'begDate<\''+unicode(self.begDate.toString('yyyy-MM-dd'))+u'\' and grouping=\'ГТС\'')
        if prevContract:
            prevContractDate=forceDate(prevContract.value(0))
            if prevContractDate:
                prevContractDateStr='\''+unicode(prevContractDate.toString('dd.MM.yyyy'))+'\''
                stmt=u'''
                    SELECT *
                    FROM VMU_TARIFF
                    JOIN VMU_PROFILE ON VMU_PROFILE.ID_PROFILE=VMU_TARIFF.ID_PROFILE
                    WHERE
                        VMU_TARIFF.TARIFF_BEGIN_DATE<'''+begDateStr+'''
                        AND VMU_TARIFF.TARIFF_BEGIN_DATE>'''+prevContractDateStr+'''
                        AND VMU_PROFILE.ID_PROFILE_TYPE=3
                        AND VMU_PROFILE.PROFILE_END_DATE>=VMU_TARIFF.TARIFF_BEGIN_DATE
                        AND VMU_PROFILE.PROFILE_BEGIN_DATE<=VMU_TARIFF.TARIFF_BEGIN_DATE'''+zone
                query = EIS_db.query(stmt)
                query.setForwardOnly(True)
                while query.next():
                    QtGui.qApp.processEvents()
                    if self.abort:
                        break
                    record = query.record()
                    PROFILE_INFIS_CODE=forceString(record.value('PROFILE_INFIS_CODE'))
                    self.err2log(PROFILE_INFIS_CODE, u'между этим контрактом и предыдущим')

        nextContract=db.getRecordEx(
            self.tblContract, '*',
            'begDate>\''+unicode(self.begDate.toString('yyyy-MM-dd'))+u'\' and grouping=\'ГТС\'')
        if not nextContract:
            stmt=u'''
                SELECT *
                FROM VMU_TARIFF
                JOIN VMU_PROFILE on VMU_PROFILE.ID_PROFILE=VMU_TARIFF.ID_PROFILE
                WHERE
                    VMU_TARIFF.TARIFF_BEGIN_DATE>'''+begDateStr+'''
                    AND VMU_PROFILE.ID_PROFILE_TYPE=3
                    AND VMU_PROFILE.PROFILE_END_DATE>=VMU_TARIFF.TARIFF_BEGIN_DATE
                    AND VMU_PROFILE.PROFILE_BEGIN_DATE<=VMU_TARIFF.TARIFF_BEGIN_DATE'''+zone
            query = EIS_db.query(stmt)
            query.setForwardOnly(True)
            while query.next():
                QtGui.qApp.processEvents()
                if self.abort:
                    break
                record = query.record()
                PROFILE_INFIS_CODE=forceString(record.value('PROFILE_INFIS_CODE'))
                self.err2log(PROFILE_INFIS_CODE, u'позже этого контракта')

        self.log.append(u'Добавлено: %d; изменено: %d' % (n_add, n_edit))
        self.log.append(u'Готово')
        self.progressBar.setValue(n-1)
        self.ok = not self.abort


    def format7Values(self, amount, price, inflectionPoint1, inflectionPointPrice1, 
                                           inflectionPoint2, inflectionPointPrice2):
            
        f1Start = f1Sum = f1Price = f2Start = f2Sum = f2Price = 0
            
        if not inflectionPoint1 is None:
            f1Start = inflectionPoint1
            f1Sum   = inflectionPoint1*inflectionPointPrice1
            f1Price = inflectionPointPrice1
            
            if not inflectionPoint2 is None:
                f2Start = inflectionPoint2
                f2Sum   = inflectionPoint2*inflectionPointPrice2
                f2Price = inflectionPointPrice2
            
        elif not inflectionPoint2 is None:
            f1Start = inflectionPoint2
            f1Sum   = inflectionPoint2*price
            f1Price = inflectionPointPrice2
            
            f2Start = 0
            f2Sum   = 0
            f2Price = 0
            
            
        return amount, price, f1Start, f1Sum, f1Price, f2Start, f2Sum, f2Price
        

    def toKnowEventTypeId(self, tariffRecord):
        db = QtGui.qApp.db
        profileName = forceString(tariffRecord.value('PROFILE_NAME'))
        idKsgGroup  = forceInt(tariffRecord.value('ID_KSG_GROUP'))
        query = self.EIS_db.query('select KSG_GROUP_NAME from VMU_KSG_GROUP where ID_KSG_GROUP=%d'%idKsgGroup)
        query.first()
        profile = forceString(query.record().value('KSG_GROUP_NAME'))
        eventTypeList = db.getRecordList('EventType', '*', 'eventProfile_id IS NOT NULL')
        eventProfileTypeList = db.getRecordList('rbEventProfile')
        eventProfileId = None
        for eventProfileType in eventProfileTypeList:
           if profile ==  forceString(eventProfileType.value('name')):
               eventProfileId = forceInt(eventProfileType.value('id'))
               break
        if not eventProfileId:
            return
        eventTypeId = None
        for eventType in eventTypeList:
            if eventProfileId == forceInt(eventType.value('eventProfile_id')):
                if profileName[0:3] == forceString(eventType.value('name'))[0:3]:
                    eventTypeId = forceInt(eventType.value('id'))
                    break
        return eventTypeId



    def calculateTariffData(self, tariffRecord, stmt):
        # Раньше для тарифов с учетом по количеству дней использовали поле amount и различные его вариации.
        # Обнаружилось, что поле amount может быть null, но в ЕИСе есть поля start_day и end_day, в которых
        # вроде как как раз лежат периоды в духе "с 3 по 7 день оплачиваются по такой-то цене". Так что вместо amount
        # пробуем использовать start_day для заполнения цен по периодам.
        QtGui.qApp.processEvents()
        db  =QtGui.qApp.db
        idProfile = forceInt(tariffRecord.value('ID_PROFILE'))
        stmt += ''' and t1.ID_PROFILE=%d'''
        query = self.EIS_db.query(stmt%('max(START_DAY)', idProfile))
        query.first()

        amount = forceDouble(query.value(0))
            
        price                 = None
        inflectionPoint1      = None
        inflectionPointPrice1 = None
        inflectionPoint2      = None
        inflectionPointPrice2 = None

        if amount > 0:
            stmt += ' order by t1.START_DAY'
            query = self.EIS_db.query(stmt%('*', idProfile))
            
            previousRecord        = None
            inflectionPoints      = []
            inflectionPointPrices = []
            prices                = []
            
            recordList = self.getActualRecordListFromQuery(query)
            previous_price_as_str = None
            first = True
            base_price = 0.0
            for record in recordList:
                    
                previousPrice = forceDouble(previousRecord.value('PRICE')) if previousRecord else 0
                price = forceDouble(record.value('PRICE')) - previousPrice
                if first:
                    currentAmount = forceInt(record.value('START_DAY'))
                    base_price = price / currentAmount if currentAmount > 1 else price
                    first = False

                price_as_str = '%.2f' % price

                if previousRecord:
                    if price_as_str != previous_price_as_str:
                        
                        inflectionPoint = forceDouble(record.value('START_DAY'))
                        inflectionPoints.append(inflectionPoint)
                        
                        currentAmount = forceDouble(record.value('START_DAY')) if forceDouble(record.value('START_DAY')) else 1
                        inflectionPointPrice = forceDouble(record.value('PRICE'))/currentAmount
                        inflectionPointPrices.append(inflectionPointPrice)

                previousRecord = record
                previous_price_as_str = price_as_str
                
            
            if base_price is None:
                return None
            
            inflectionPoint1      = inflectionPoints[0]       if len(inflectionPoints)      else None
            if inflectionPoint1:
                inflectionPointPrice1 = inflectionPointPrices[0]  if len(inflectionPointPrices) else None
            else:
                inflectionPointPrice1 = inflectionPoint1 = None
            
            inflectionPoint2      = inflectionPoints[-1]      if len(inflectionPoints)      else None
            if inflectionPoint2:
                inflectionPointPrice2 = inflectionPointPrices[-1] if len(inflectionPointPrices) else None
            else:
                inflectionPointPrice2 = inflectionPoint2 = None
            
            if inflectionPoint1 == inflectionPoint2:
                inflectionPoint2 = inflectionPointPrice2 = None
            return amount, base_price, inflectionPoint1, inflectionPointPrice1, inflectionPoint2, inflectionPointPrice2
            
        return None
        
        
    def getActualRecordListFromQuery(self, query):
        result = []
        go = query.first()
        _tariffBegDateMap = {}
        while go:
            record = query.record()
            tbd = unicode(forceDate(record.value('TARIFF_BEGIN_DATE')).toString('yyyy.MM.dd'))
            tariffBegDateRecordList = _tariffBegDateMap.setdefault(tbd, [])
            tariffBegDateRecordList.append(record)
            
            go = query.next()
        
        keys = _tariffBegDateMap.keys()
        if keys:
            maxTBD = max(keys)
            return _tariffBegDateMap[maxTBD]
        return []
            
        

    def err2log(self, infisServiceCode, message):
        note=u''
        begDate=forceDate(QtGui.qApp.db.translate('rbService', 'infis', infisServiceCode, 'begDate'))
        endDate=forceDate(QtGui.qApp.db.translate('rbService', 'infis', infisServiceCode, 'endDate'))
        if begDate:
            note=u' (с '+forceString(begDate)
            if endDate:
                note+=u' по '+forceString(endDate)
            note+=u')'
        self.log.append(u'тариф '+infisServiceCode+note+u' '+message)
