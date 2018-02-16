# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

u"""
Импорт тарифа из Тер. фонда.
"""
import re

from PyQt4 import QtCore, QtGui

from Accounting.Utils   import CTariff
from library.AgeSelector import parseAgeSelector
from library.Utils      import forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, getVal, toVariant
from library.dbfpy      import dbf

from Orgs.TariffModel   import CTariffModel

from Cimport            import CImport, CDBFimport
from Utils              import tbl
from Ui_ImportTariffsUniversal import Ui_Dialog


def ImportTariffsR23(widget, contractId, begDate, endDate, tariffList):
    dlg=CImportTariffs(widget, contractId, begDate, endDate, tariffList)
    dlg.setWindowTitle(u'Загрузка тарифов для Краснодарского края')
    
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR23FileName',  '')))
    
    dlg.priceField = 'TARIF'
    # dlg.compositionExpenseCongruenceInfo = {'TARIF_B' : '1',
    #                                         'TARIF_D' : '2',
    #                                         'TARIF_DM' : '3',
    #                                         'TARIF_UC' : '4'}
    dlg.compositionExpenseCongruenceInfo = {}
    dlg.fileServiceField = 'KUSL'
    dlg.begDateField = 'DATN'
    dlg.endDateField = 'DATO'

    dlg.addImportType(tariffTypeCode = 2, 
                      medicalAidUnitCode = '2', 
                      amount = 0, 
                      fillEventType = False, 
                      sourceServiceCodeChecker = lambda dbfRecord  : bool(re.match(ur'^[KkКк].+', forceString(dbfRecord['KUSL']))),
                      sourceServiceCodeCheckerDescr = u'Все услуги, код которых начинается на \'K\'',
                      alias = u'Койко-дни')
    
    dlg.addImportType(tariffTypeCode = 2, 
                      medicalAidUnitCode = '2', 
                      amount = 0, 
                      fillEventType = False, 
                      sourceServiceCodeChecker = lambda dbfRecord  : bool(re.match(ur'^[^SsKkКкGgVv].+', forceString(dbfRecord['KUSL']))),
                      sourceServiceCodeCheckerDescr = u'Все услуги, код которых начинается НЕ на \'K\' и НЕ на \'S\'',
                      alias = u'Услуги')
    
    dlg.addImportType(tariffTypeCode = 10,
                      medicalAidUnitCode = '3', 
                      amount = 1, 
                      fillEventType = True,
                      sourceServiceCodeChecker = lambda dbfRecord  : bool(re.match(ur'^[Ss].+', forceString(dbfRecord['KUSL']))),
                      sourceServiceCodeCheckerDescr = u'Все услуги, код которых начинается на \'S\'',
                      alias = u'Стандарты')

    dlg.addImportType(tariffTypeCode = 13,
                      medicalAidUnitCode = '3',
                      amount = 0,
                      fillEventType = True,
                      sourceServiceCodeChecker = lambda dbfRecord  : bool(re.match(ur'^[GgVv].+', forceString(dbfRecord['KUSL']))),
                      sourceServiceCodeCheckerDescr = u'Все услуги, код которых начинается на \'G\' или \'V\'',
                      alias = u'Стандарты по КСГ')
    
    dlg.exec_()
    isOk =  not dlg.abort
    QtGui.qApp.preferences.appPrefs['ImportTariffR23FileName'] = toVariant(dlg.edtFileName.text())
    return isOk, dlg.tariffList


def ImportTariffsR61(widget, contractId, begDate, endDate, tariffList):
    dlg=CImportTariffs(widget, contractId, begDate, endDate, tariffList)
    dlg.setWindowTitle(u'Загрузка тарифов для Ростовской области')
    
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR61FileName',  '')))
    
    dlg.priceField = 'STOIM'
    dlg.compositionExpenseCongruenceInfo = {'ZPL' : '1',
                                            'MED' : '2',
                                            'M_INV' : '3',
                                            'KOS' : '4',
                                            'NAKL' : '5',
                                            'DOPL' : '6'}
    dlg.fileServiceField = 'KSPEC'
    dlg.begDateField = 'DATAN'
    dlg.endDateField = 'DATAK'
    
    
    dlg.addImportType(tariffTypeCode = 0, 
                      medicalAidUnitCode = '25', 
                      amount = 0, 
                      fillEventType = False, 
                      alias = u'Визиты')
    
    dlg.exec_()
    isOk =  not dlg.abort
    QtGui.qApp.preferences.appPrefs['ImportTariffR61FileName'] = toVariant(dlg.edtFileName.text())
    return isOk, dlg.tariffList


def ImportTariffsR51(widget, contractId, begDate, endDate, tariffList):
    dlg=CImportTariffs(widget, contractId, begDate, endDate, tariffList)
    dlg.setWindowTitle(u'Загрузка тарифов для Мурманской области')
    
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR51FileName',  '')))
    
    dlg.priceField = 'TARIF_A'
    dlg.compositionExpenseCongruenceInfo = {'TARIF_A1' : '1',
                                            'TARIF_A2' : '2',
                                            'TARIF_A3' : '3',
                                            'TARIF_A4' : '4',
                                            'TARIF_A6' : '5'}
    dlg.fileServiceField = 'PROF'
    dlg.begDateField = 'TARIF_DATE'
    dlg.endDateField = 'D_TO'
    dlg.fileSpecialityField = 'SPEC'
    dlg.dbSpecialityFieldRule = [('rbSpeciality', 'regionalCode', 'id')]
    
    
    dlg.addImportType(tariffTypeCode = 0, #посещение
                      medicalAidUnitCode = None, 
                      amount = 0, 
                      fillEventType = False, 
                      alias = u'Услуги (по посещению)')
    
    dlg.addImportType(tariffTypeCode = 2, #мероприятие по количеству
                      medicalAidUnitCode = None, 
                      amount = 0,
                      age = u'-17г',
                      fillEventType = False, 
                      alias = u'Флюорография детская (мероприятие по кол-ву)',
                      sourceServiceCodeChecker = lambda dbfRecord  : bool(re.match(ur'\s*060951[0-5]00\s*', forceString(dbfRecord['PROF']))), #atronah: i1009.c2837
                      sourceServiceCodeCheckerDescr = u'Все услуги с кодами из списка (060951000, 060951100, 060951200, 060951300, 060951400, 060951500)', 
                      fileFieldsInfo = {'priceField' : 'CHLD_TARIF'},
                      compositionExpenseCongruenceInfo = {'TARIF_5' : '1',
                                                          'TARIF_6' : '2',
                                                          'TARIF_7' : '3',
                                                          'TARIF_8' : '4',
                                                          'TARIF_81' : '5'})
    
    dlg.addImportType(tariffTypeCode = 2, #мероприятие по количеству
                      medicalAidUnitCode = None, 
                      amount = 0,
                      age = u'18г-',
                      fillEventType = False, 
                      alias = u'Мероприятие по кол-ву',
                      fileFieldsInfo = {'priceField' : 'PROF_TARIF'},
                      compositionExpenseCongruenceInfo = {'TARIF_1' : '1',
                                                          'TARIF_2' : '2',
                                                          'TARIF_3' : '3',
                                                          'TARIF_4' : '4',
                                                          'TARIF_41' : '5'})
    
    
    
    
    #atronah: i1032.c2900
    serviceCodeListForExcludeThirdExpense = [u'0А1200', u'0А1210', u'0А1700', u'1Г0200', u'1Д0700'
                                            , u'2Д0100', u'2Д0200', u'2Д0300', u'2Д0610', u'2Е0310'
                                            , u'2Е3200', u'2Е0201', u'2Е0202', u'2Е3400', u'2Е4042'
                                            , u'2Е4043', u'2Е4044', u'2Е5003', u'2Е5004', u'2Е5005']
    
    dlg.addImportType(alias = u'Обновление всех тарифов по базовой услуге\n(БЕЗ учета статьи затрат с кодом \'3\')',
                      compositionExpenseCongruenceInfo = {'TARIF_A1' : '1',
                                                          'TARIF_A2' : '2',
                                                          'TARIF_A5' : '4',
                                                          'TARIF_A6' : '5'},
                      sourceServiceCodeChecker = lambda dbfRecord  :  forceString(dbfRecord['PROF']) in serviceCodeListForExcludeThirdExpense, 
                      sourceServiceCodeCheckerDescr = u'Все услуги с кодом из списка: (%s)' % ', '.join(serviceCodeListForExcludeThirdExpense),
                      isUpdateTariffViaBaseService = True)
    
    dlg.addImportType(alias = u'Обновление всех тарифов по базовой услуге\n(С учетом статьи затрат с кодом \'3\')',
                      compositionExpenseCongruenceInfo = {'TARIF_A1' : '1',
                                                          'TARIF_A2' : '2',
                                                          'TARIF_A3' : '3',
                                                          'TARIF_A5' : '4',
                                                          'TARIF_A6' : '5'},
                      sourceServiceCodeChecker = lambda dbfRecord  :  forceString(dbfRecord['PROF']) not in serviceCodeListForExcludeThirdExpense, 
                      sourceServiceCodeCheckerDescr = u'Все кроме услуг с кодом из списка: (%s)' % ', '.join(serviceCodeListForExcludeThirdExpense),
                      isUpdateTariffViaBaseService = True)
    
    
    #i1046
    dlg.addImportType(tariffTypeCode = 10, #событие по МЭС и длительности
                      medicalAidUnitCode = None, 
                      amount = 0,
                      fillEventType = True, 
                      alias = u'Дневной стационар',
                      fileFieldsInfo = {'priceField' : 'PRICE_DAY1',
                                        'begDateField' : 'DAT_B',
                                        'endDateField' : 'DAT_E',
                                        'fileSpecialityField' : u'',
                                        'dbServiceFieldRule' : [('mes.MES', 'descr', 'code'), ('rbService', 'code', 'id')]},
                      sourceServiceCodeChecker = lambda dbfRecord  : forceString(dbfRecord['CODE_HOSP']) == '606', 
                      sourceServiceCodeCheckerDescr = u'Все тарифы с CODE_HOSP = 606',
                      compositionExpenseCongruenceInfo = {'TARIF_A11' : '1', #заработная плата
                                                          'TARIF_A22' : '2', #начисления на з/плату 
                                                          'TARIF_A33' : '3', #ЛС, РМ и ИМН
                                                          'TARIF_A55' : '4', #мягкий инвентарь
                                                          'TARIF_A66' : '5'},
                      isUpdateFrag1Start = True) #иные расходы
    #i1046
    dlg.addImportType(tariffTypeCode = 10, #событие по МЭС и длительности
                      medicalAidUnitCode = None, 
                      amount = 0,
                      fillEventType = True, 
                      alias = u'Центр реабилитации',
                      fileFieldsInfo = {'priceField' : 'PRICE_DAY1',
                                        'begDateField' : 'DAT_B',
                                        'endDateField' : 'DAT_E',
                                        'fileSpecialityField' : u'',
                                        'dbServiceFieldRule' : [('mes.MES', 'descr', 'code'), ('rbService', 'code', 'id')]},
                      sourceServiceCodeChecker = lambda dbfRecord  : forceString(dbfRecord['CODE_HOSP']) == '825', 
                      sourceServiceCodeCheckerDescr = u'Все тарифы с CODE_HOSP = 825',
                      compositionExpenseCongruenceInfo = {'TARIF_A11' : '1', #заработная плата
                                                          'TARIF_A22' : '2', #начисления на з/плату 
                                                          'TARIF_A33' : '3', #ЛС, РМ и ИМН
                                                          'TARIF_A55' : '4', #мягкий инвентарь
                                                          'TARIF_A66' : '5'},
                      isUpdateFrag1Start = True) #иные расходы
    
    #i1046
    dlg.addImportType(tariffTypeCode = 10, #событие по МЭС и длительности
                      medicalAidUnitCode = None, 
                      amount = 0,
                      fillEventType = True, 
                      alias = u'Cтационар на дому',
                      fileFieldsInfo = {'priceField' : 'PRICE_DAY1',
                                        'begDateField' : 'DAT_B',
                                        'endDateField' : 'DAT_E',
                                        'fileSpecialityField' : u'',
                                        'dbServiceFieldRule' : [('mes.MES', 'descr', 'code'), ('rbService', 'code', 'id')]},
                      sourceServiceCodeChecker = lambda dbfRecord  : forceString(dbfRecord['CODE_HOSP']) == '143', 
                      sourceServiceCodeCheckerDescr = u'Все тарифы с CODE_HOSP = 143',
                      compositionExpenseCongruenceInfo = {'TARIF_A11' : '1', #заработная плата
                                                          'TARIF_A22' : '2', #начисления на з/плату 
                                                          'TARIF_A33' : '3', #ЛС, РМ и ИМН
                                                          'TARIF_A55' : '4', #мягкий инвентарь
                                                          'TARIF_A66' : '5'},
                      isUpdateFrag1Start = True) #иные расходы

    dlg.exec_()
    isOk =  not dlg.abort
    QtGui.qApp.preferences.appPrefs['ImportTariffR51FileName'] = toVariant(dlg.edtFileName.text())
    return isOk, dlg.tariffList

def ImportTariffsR85(widget, contractId, begDate, endDate, tariffList):
    dlg=CImportTariffs(widget, contractId, begDate, endDate, tariffList)
    dlg.setWindowTitle(u'Загрузка тарифов для Республики Крым')

    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR85FileName',  '')))

    dlg.priceField = 'PRICE'
    dlg.federalPriceField = 'PRICE_F'
    dlg.fileServiceField = 'SERVICE'
    dlg.begDateField = 'BEGDATE'
    dlg.endDateField = 'ENDDATE'
    dlg.uetField = 'UET'
    dlg.frag1StartField = 'AMOUNT_1'
    dlg.frag1SumField = 'PRICE_1'
    dlg.unitField = 'UNIT'
    dlg.ageField = 'AGE'


    dlg.addImportType(tariffTypeCode=CTariff.ttVisit, # посещение
                      medicalAidUnitCode = None,
                      alias=u'Амбулаторное посещение',
                      amount=0,
                      fillEventType=False,
                      sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] == '3.',
                      sourceServiceCodeCheckerDescr = u'Все тарифы с кодом на 3.*',
    )
    # dlg.addImportType(tariffTypeCode = CTariff.ttEventByMESLen, #событие по МЭС и длительности
    #                   medicalAidUnitCode = None,
    #                   amount = 0,
    #                   fillEventType = True,
    #                   distinctEventType = True,
    #                   alias = u'Круглосуточный стационар',
    #                   sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] == '1.',
    #                   sourceServiceCodeCheckerDescr = u'Все тарифы с кодами на 1.* и 2.*',
    #                   )
    # dlg.addImportType(tariffTypeCode = CTariff.ttEventByMESLen, #событие по МЭС и длительности
    #                   medicalAidUnitCode = None,
    #                   amount = 0,
    #                   fillEventType = True,
    #                   distinctEventType = True,
    #                   alias = u'Дневной стационар',
    #                   sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] in '2.',
    #                   sourceServiceCodeCheckerDescr = u'Все тарифы с кодами на 1.* и 2.*',
    #                   )
    dlg.addImportType(tariffTypeCode=CTariff.ttEventByMESLen, #событие по МЭС и длительности
                      medicalAidUnitCode = None,
                      amount = 0,
                      fillEventType = True,
                      distinctEventType = True,
                      alias = u'Cтационар',
                      sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE']).isdigit()
                                                                    and 1 <= int(forceString(dbfRecord['SERVICE'])) <= 37 ,
                      sourceServiceCodeCheckerDescr = u'Все тарифы с кодами в диапазоне 1 - 37',
                      )
    dlg.addImportType(tariffTypeCode = CTariff.ttVisitByActionUET,
                      medicalAidUnitCode = None,
                      amount = 0,
                      fillEventType = False,
                      alias = u'Стоматологическое посещение',
                      sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] == '3.',
                      sourceServiceCodeCheckerDescr = u'Все тарифы с кодами на 3.*'
                      )
    dlg.addImportType(tariffTypeCode = CTariff.ttActionUET,
                      medicalAidUnitCode = None,
                      amount = 0,
                      fillEventType = False,
                      alias = u'Стоматологические услуги',
                      sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] == '63',
                      sourceServiceCodeCheckerDescr = u'Все тарифы с кодами на 63*'
                      )
    dlg.addImportType(tariffTypeCode = CTariff.ttActionAmount,
                      medicalAidUnitCode = None,
                      amount = 0,
                      fillEventType = True,
                      distinctEventType = True,
                      alias = u'Услуги',
                      sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] != '63'
                                                                    and forceString(dbfRecord['SERVICE'])[:2] != '3.'
                                                                    and not (forceString(dbfRecord['SERVICE']).isdigit()
                                                                            and 1 <= int(forceString(dbfRecord['SERVICE'])) <= 37),
                      sourceServiceCodeCheckerDescr = u'Все тарифы, не входящие в остальные категории'
                      )
    dlg.addImportType(tariffTypeCode = CTariff.ttEventByMESLen,
                      medicalAidUnitCode = None,
                      amount = 1,
                      fillEventType = True,
                      distinctEventType = True,
                      alias = u'Диспансеризация',
                      sourceServiceCodeChecker = lambda dbfRecord: forceString(dbfRecord['SERVICE'])[:2] in ('50', '70'),
                      sourceServiceCodeCheckerDescr = u'Все тарифы с кодами на 50* или 70*'
                      )
    dlg.addImportType(tariffTypeCode = CTariff.ttEventByHTG,
                      medicalAidUnitCode = None,
                      amount = 0,
                      fillEventType = True,
                      distinctEventType = True,
                      alias = u'ВМП',
                      sourceServiceCodeChecker = lambda dbfRecord: bool(re.match(u'^\d\d\.\d\d\.\d\d?\.\d\d\d$', forceString(dbfRecord['SERVICE']))),
                      sourceServiceCodeCheckerDescr = u'Все тарифы с кодом в формате 00.00.00.000'
                      )
    dlg.exec_()
    isOk =  not dlg.abort
    QtGui.qApp.preferences.appPrefs['ImportTariffR85FileName'] = toVariant(dlg.edtFileName.text())
    return isOk, dlg.tariffList


class CImportTariffs(QtGui.QDialog, Ui_Dialog, CDBFimport):
    precision = 0.001
    
    serviceCache = {}
    specialityCache = {}
    unitCache = {}
    
    priceField = 'TARIF'
    federalPriceField = None
    frag1StartField = None
    frag1SumField = None
    uetField = None
    unitField = None
    
    fileServiceField = 'KUSL'
    dbServiceFieldRule = [('rbService', 'code', 'id')]
    
    begDateField = 'DATN'
    endDateField = 'DATO'
    
    fileSpecialityField = None
    dbSpecialityFieldRule = [('rbSpeciality', 'code', 'id')]

    fileUnitField = None
    dbUnitFieldRule = [('rbMedicalAidUnit', 'code', 'id')]
    
    ageField = None
    
    class DataType:
        Service = 0
        Speciality = 1
        Unit = 2
    
    def __init__(self,  parent, contractId, begDate, endDate, tariffList):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        
        self.progressBar.setFormat('%v')
        self.parent = parent
        self.contractId = contractId
        self.begDate = begDate
        self.endDate = endDate
        self.tariffList = list(reversed(tariffList))
        self.mapCompositionExpenseFieldNameToId = {}
        self.mapServiceIdToUet = {}
        
        self.tableContractTariff = tbl('Contract_Tariff')
        self.tariffIdxByServiceAndSpecialityId = {}
        for i, tariff in enumerate(self.tariffList):
            key = (forceRef(tariff.value('service_id')),
                   forceRef(tariff.value('speciality_id')))
            self.tariffIdxByServiceAndSpecialityId.setdefault(key, []).append(i)

        # Сортировка тарифов на услугу по убыванию даты начала
        for value in self.tariffIdxByServiceAndSpecialityId.values():
            value.sort(lambda x, y: 1 if forceDate(self.tariffList[x].value('begDate')) > forceDate(self.tariffList[y].value('begDate')) 
                                      else 0 if forceDate(self.tariffList[x].value('begDate')) == forceDate(self.tariffList[y].value('begDate'))
                                             else -1,
                        reverse = True)
            
        self.duplicateBehavior = QtGui.QButtonGroup(self)
        self.duplicateBehavior.addButton(self.chkUpdate, 0)
        self.duplicateBehavior.addButton(self.chkSkip, 1)
        self.duplicateBehavior.addButton(self.chkAskUser, 2)
        self.chkUpdate.setChecked(True)
        
        self.importTypeButtons = QtGui.QButtonGroup(self)
        self.connect(self.importTypeButtons, QtCore.SIGNAL('buttonClicked(int)'), self.onImportTypeChanged)
        self.importTypeList = []
        self.compositionExpenseCongruenceInfo = {}
        
        self.cmbMedicalAidUnit.setTable('rbMedicalAidUnit', True)
        self.cmbMedicalAidUnit.setValue(None)
        
        self.cmbTariffType.addItems(CTariffModel.tariffTypeNames)
        
        self.edtBegDate.canBeEmpty(True)
        self.edtEndDate.canBeEmpty(True)
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)
        
        self.cmbEventType.setTable('EventType', True)
        self.cmbEventType.setCode(None)

        self.age = None

        self.resetState()

    ## Добавление поддерживаемого типа импорта тарифов на форму импорта
    # @param defaultTariffType: код (целое число) типа тарифа по умолчанию, соответствующий индексу в массиве CTariffModel.tariffTypeNames
    #    (может измениться, лучше проверять в файле Orgs.Contracts.py)
    #        0: посещение
    #        1: событие
    #        2: мероприятие по количеству
    #        3: визит-день
    #        4: событие по койко-дням
    #        5: мероприятие по УЕТ
    #        6: мероприятие по количеству и тарифу койки
    #        7: визиты по мероприятию
    #        8: визиты по МЭС
    #        9: событие по МЭС
    #        10: событие по МЭС и длительности
    # @param medicalAidUnitCode: код (строка) единицы учета тарифа из таблицы бд rbMedicalAidUnit
    # @param amount: количество, проставляемое в тарифе
    # @param age: интервал возрастов, устанавливаемый для обрабатываемых тарифов (формат согласно полю БД Contract_Tariff.age)
    #            Применимо для указанного интервала возрастов пусто-нет ограничения, 
    #                "{NNN{д|н|м|г}-{MMM{д|н|м|г}}" - с NNN дней/недель/месяцев/лет по MMM дней/недель/месяцев/лет; 
    #                пустая нижняя или верхняя граница - нет ограничения снизу или сверху
    # atronah: если появится необходимость более тонкой настройки типов события, то все доп. опции можно добавить отдельными виджетами на форму и включать их через fillEventType 
    # @param fillEventType: флаг, включающий возможность выбора типа события, которое будет проставляться для тарифа (если выключено, то тип события не проставляется)
    # @param distinctEventType: флаг, проверяющий соответствие по типу события при попытке обновления тарифа
    # @param sourceServiceCodeChecker: функция, принимающая на вход строку, содержащую код услуги, и возвращающая True, если услугу стоит обрабатывать, False, если стоит пропустить.
    # @param sourceServiceCodeCheckerDescr: описание функции проверки кода услуги
    # @param alias: имя элемента интерфейса для этого типа тарифа, если не указано, то ставится имя CTariffModel.tariffTypeNames[code] 
    # @param sourceFieldInfo: словарь с указанием соответствия данных и имен полей в исходном файле. Если не указан, то берутся общие для импорта имена полей.
    #            Содержание словаря:
    #                'priceField' - имя поля с данными о цене тарифа
    #                'fileServiceField' - имя поля с данными об услуге
    #                'dbServiceFieldRule' - правило для получения ID услуги по значению, полученному из файла список из кортежей вида (tableName, compareField, resultField)
    #                                       логика кортежей соответствует аргументам функции CDatabase.translate()
    #                'begDateField' - имя поля с датой начала тарифа
    #                'endDateField' - имя поля с датой окончания тарифа
    #                'fileSpecialityField' - имя поля исходного файла с кодом/идентификатором специальности
    #                'dbSpecialityFieldRule' - правило для получения ID специальности по значению, полученному из файла (@see dbServiceFieldRule)
    # @param compositionExpenseCongruenceInfo: словарь с заданием собственных настроек исходных полей
    #            (<поле_исх_файла_со_статьей_затрат> : <код_соотв-ей_статьи_затрат_в_бд>) 
    #            для статей затрат (если они отличаются от общих для импорта)
    # @param isUpdateTariffViaBaseService - обновлять тарифы на основе базовой услуги
    # @param isUpdateFrag1Start: Обновлять начало фрагмента для МЭС (выставлять туда макс. продолжительность) 
    def addImportType(self, tariffTypeCode=0, medicalAidUnitCode=None, amount=0, age=None, fillEventType=False,
                      distinctEventType=False, sourceServiceCodeChecker=None, sourceServiceCodeCheckerDescr=None,
                      alias=None, fileFieldsInfo=None, compositionExpenseCongruenceInfo=None,
                      isUpdateTariffViaBaseService=False, isUpdateFrag1Start=False, isFillUET=False):
        if not fileFieldsInfo:
            fileFieldsInfo = {}
        if not compositionExpenseCongruenceInfo:
            compositionExpenseCongruenceInfo = {}
        assert isinstance(tariffTypeCode, int) and tariffTypeCode in xrange(len(CTariffModel.tariffTypeNames))
        importTypeInfo = {}
        importTypeInfo['defaultTariffType'] = tariffTypeCode
        importTypeInfo['alias'] = alias if alias else CTariffModel.tariffTypeNames[tariffTypeCode]
        importTypeInfo['unitCode'] = medicalAidUnitCode
        importTypeInfo['amount'] = amount
        importTypeInfo['age'] = age
        importTypeInfo['fillEventType'] = fillEventType
        importTypeInfo['distinctEventType'] = distinctEventType
        importTypeInfo['serviceCodeChecker'] = sourceServiceCodeChecker
        importTypeInfo['sourceServiceCodeCheckerDescr'] = sourceServiceCodeCheckerDescr
        importTypeInfo['button'] = QtGui.QRadioButton(importTypeInfo['alias'], self.gbTariffType)
        importTypeInfo['fileFieldsInfo'] = fileFieldsInfo
        importTypeInfo['compositionExpenseCongruenceInfo'] = compositionExpenseCongruenceInfo
        importTypeInfo['isUpdateTariffViaBaseService'] = isUpdateTariffViaBaseService
        importTypeInfo['isUpdateFrag1Start'] = isUpdateFrag1Start
        importTypeInfo['isFillUET'] = isFillUET
#        toolTip = '\n'.join([u'Наименование: "%s"' % importTypeInfo['alias'],
#                             u'Тарифицируется: "%s"' % CTariffModel.tariffTypeNames[tariffTypeCode],
#                             u'Код ед. учета по умолчанию: %s' % medicalAidUnitCode,
#                             u'Количество: %s' % amount,
#                             u'Шаблон кода услуги: "%s"' % sourceServiceCodeChecker])
        
        importTypeIdx = len(self.importTypeList)
        
        gbLayout = self.gbTariffType.layout()
        gbLayout.addWidget(importTypeInfo['button'])
        
        self.importTypeList.append(importTypeInfo)
        importTypeInfo['button'].setToolTip(self.importTypeHtmlInfo(importTypeIdx))
        
        self.importTypeButtons.addButton(importTypeInfo['button'], importTypeIdx)
        importTypeInfo['button'].setChecked(True)
        self.onImportTypeChanged(importTypeIdx)

    
    ## Проверяет, необходимо ли загружать тариф на услугу с учетом выбранного типа тарифов (по указанному шаблону регулярного выражения для типа тарифа)
    def isLoadTariff(self, checkingDataSource):
        currentImportTypeIdx = self.importTypeButtons.checkedId()
        checker = self.importTypeList[currentImportTypeIdx]['serviceCodeChecker']
        if callable(checker):
            return checker(checkingDataSource)
        return True
    
    
    ## Добавляет соответствие поля исходного DBF определенной статье затрат
    # @param dbfFieldName: имя поля обрабатываемого DBF файла, содержащее значение статьи затрат
    # @param expenseReviceItemCode: код статьи затрат из таблицы бд rbExpenseServiceItem, соответствующее затрате в поле dbfFieldName 
    def addCompositionExpenseCongruence(self, dbfFieldName, expenseReviceItemCode):
        self.compositionExpenseCongruence[dbfFieldName] = forceRef(QtGui.qApp.db.translate('rbExpenseServiceItem', 'code', expenseReviceItemCode, 'id'))
    

    def resetState(self):
        self.abort = False
        self.counter ={'skipped' : 0,
                       'added' : 0,
                       'updated' : 0,
                       'processed' : 0}
        
        self.unitId = None
        self.amount = 0
        
    
    def importTypeHtmlInfo(self, importTypeIdx):
        if importTypeIdx not in xrange(len(self.importTypeList)):
            return u'''<h3>Ошибка получения данных по типу импорта</h3>'''
        
        importType = self.importTypeList[importTypeIdx]
        
        
        fileFieldsInfo = self.importTypeList[importTypeIdx].get('fileFieldsInfo', {})
        
        currentCompositionExpenseCongruenceInfo = importType['compositionExpenseCongruenceInfo'] or self.compositionExpenseCongruenceInfo
        compositionExpenseList = []
        for fieldName in sorted(currentCompositionExpenseCongruenceInfo.keys()):
            expenseReviceItemCode = currentCompositionExpenseCongruenceInfo.get(fieldName, None)
            compositionExpenseList.append(u'<li><span class="bold">%(fieldName)s</span> - статья затрат с кодом %(code)s</li>' % {'fieldName' : fieldName,
                                                                                                                                 'code' : expenseReviceItemCode})
        
        compositionExpenseBlock = u'''
            <li>Статьи затрат услуг:
                <ul>
                    %s
                </ul>
            </li>
            ''' % u'\n'.join(compositionExpenseList) if compositionExpenseList else u''
        
        htmlInfo = u'''
                        <body>
                            <style type="text/css">
                                span.bold {font-weight:bold}
                            </style>
                        
                        <h3>Информация по типу импорта</h3>
                        <p><span class="bold">Название:</span> %(alias)s</p>
                        <p><span class="bold">Тарифицируется:</span> %(tariffType)s</p>
                        <p><span class="bold">Количество по умолчанию:</span> %(amount)s</p>
                        <p><span class="bold">Код ед. учета медицинской помощи по умолчанию:</span> %(medicalAidUnitCode)s</p> 
                        <p><span class="bold">Возрастное ограничение:</span> %(age)s</p>
                        <p><span class="bold">Заполнять тип события:</span> %(fillEventType)s</p>
                        <p><span class="bold">Шаблон кода услуги:</span> %(serviceCodeCheckerDescr)s</p>
                        <br />
                        <h3>Информация о требуемом для импорта файле</h3>
                        <p><span class="bold">Тип файла:</span> DBF</p>
                        <p>
                            <span class="bold">Список полей и их назначение:</span> 
                            <ul>
                                <li><span class="bold">%(price)s</span> - основная цена</li>
                                <li><span class="bold">%(serviceCode)s</span> - услуга (правило поиска в базе: %(dbServiceCode)s)</li>
                                <li><span class="bold">%(speciality)s</span> - специальность (правило поиска в базе: %(dbSpeciality)s)</li>
                                <li><span class="bold">%(begDate)s</span> - дата начала действия тарифа</li>
                                <li><span class="bold">%(endDate)s</span> - дата окончания действия тарифа</li>
                                %(compositionExpenseBlock)s
                            </ul>
                        </p>
                        </body>
        ''' % {'alias' : importType.get('alias', u'-'),
               'tariffType' : CTariffModel.tariffTypeNames[importType['defaultTariffType']],
               'amount' : importType.get('amount', u'-'),
               'medicalAidUnitCode' : importType.get('unitCode', u'-'),
               'age' : importType.get('age', u'-'),
               'fillEventType' : u'Да' if importType.get('fillEventType', False) else u'Нет',
               'serviceCodeCheckerDescr' : importType.get('serviceCodeCheckerDescr', (None, None))[0] or u'-',
               
               'price' : fileFieldsInfo.get('priceField', None) or self.priceField,
               'serviceCode' : fileFieldsInfo.get('fileServiceField', None) or self.fileServiceField,
               'dbServiceCode' : fileFieldsInfo.get('dbServiceFieldRule', None) or self.dbServiceFieldRule, 
               'speciality'  : fileFieldsInfo.get('fileSpecialityField', None) or self.fileSpecialityField,
               'dbSpeciality' : fileFieldsInfo.get('dbSpecialityFieldRule', None) or self.dbSpecialityFieldRule,
               'begDate' : fileFieldsInfo.get('begDateField', None) or self.begDateField,
               'endDate' : fileFieldsInfo.get('endDateField', None) or self.endDateField,
               
               'compositionExpenseBlock' : compositionExpenseBlock}
        return htmlInfo


    def currentImportTypeHtmlInfo(self):
        currentImportTypeIdx = self.importTypeButtons.checkedId()
        return self.importTypeHtmlInfo(currentImportTypeIdx)
    
    
    def beforeStart(self):
        self.resetState()
        self.gbTariffParameters.setEnabled(False)
        self.gbPeriod.setEnabled(False)
        self.gbDublicates.setEnabled(False)
        self.gbTariffType.setEnabled(False)
        
    
    
    def afterEnd(self):
        self.gbTariffParameters.setEnabled(True)
        self.gbPeriod.setEnabled(True)
        self.gbDublicates.setEnabled(True)
        self.gbTariffType.setEnabled(True)
        
        if hasattr(self, 'dbfTariff'):
            self.dbfTariff.close() 
        self.log.append(u'добавлено: %(added)d; изменено: %(updated)d' % self.counter)
        self.log.append(u'пропущено: %(skipped)d; обработано: %(processed)d' % self.counter)
        self.log.append(u'готово')
        
    
    
    def startImport(self):
        contractId = self.contractId
        if not contractId:
            return
        
        self.serviceCache.clear()
        self.specialityCache.clear()
        self.unitCache.clear()
        
        dbfFileName = forceStringEx(self.edtFileName.text())
        self.dbfTariff = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        
        currentImportTypeIdx = self.importTypeButtons.checkedId()
        
        self.fileFieldsInfo = self.importTypeList[currentImportTypeIdx].get('fileFieldsInfo', {})
        self.amount = self.importTypeList[currentImportTypeIdx]['amount']
        self.defaultAge = self.importTypeList[currentImportTypeIdx]['age']
        self.unitId = self.cmbMedicalAidUnit.value()
        self.eventTypeId = self.cmbEventType.value() if self.importTypeList[currentImportTypeIdx]['fillEventType'] else None
        self.distinctEventType = self.importTypeList[currentImportTypeIdx].get('distinctEventType', False)
        self.tariffType = self.cmbTariffType.currentIndex()
        self.fillUET = self.chkFillUET.isChecked()
        self.mapServiceIdToUet = {}
        self.begDate = self.edtBegDate.date() if self.edtBegDate.date().isValid() else None
        self.endDate = self.edtEndDate.date() if self.edtEndDate.date().isValid() else None
        self.isUpdateFrag1Start = self.importTypeList[currentImportTypeIdx].get('isUpdateFrag1Start', False)
        
        if self.begDate and self.endDate and (self.begDate> self.endDate):
            self.log.append(u'<b><font color=red>ОШИБКА:</b> Неверно задан период.')
            self.abort = True
            return
        
        self.mapCompositionExpenseFieldNameToId = {}
        currentCompositionExpenseCongruenceInfo = self.importTypeList[currentImportTypeIdx]['compositionExpenseCongruenceInfo'] or self.compositionExpenseCongruenceInfo
        for fieldName in set(currentCompositionExpenseCongruenceInfo.keys()): 
            expenseReviceItemCode = currentCompositionExpenseCongruenceInfo.get(fieldName, None)
            self.mapCompositionExpenseFieldNameToId[fieldName] = forceRef(QtGui.qApp.db.translate('rbExpenseServiceItem', 'code', expenseReviceItemCode, 'id'))

        if self.importTypeList[currentImportTypeIdx]['isUpdateTariffViaBaseService']:
            self.baseServiceDbfRow = None
            begDateField = self.fileFieldsInfo['begDateField'] if self.fileFieldsInfo.has_key('begDateField') else self.begDateField
            # atronah: поиск среди всех записей исходного файла
            # самой "свежей" среди соответствующих выбранному периоду дат
            for dbfRow in self.dbfTariff:
                baseDate = forceDate(dbfRow[begDateField])
                if self.begDate <= baseDate <= self.endDate:
                    if not self.baseServiceDbfRow or baseDate >= self.baseServiceDbfRow:
                        self.baseServiceDbfRow = dbfRow
            
            if self.baseServiceDbfRow:
                self.serviceCodeCache = {}
                self.uetCache = {}
                self.totalPrice = 0.0
                for dbfFieldName, expenceServiceItemId in self.mapCompositionExpenseFieldNameToId.items():
                    if not expenceServiceItemId:
                        self.log.append(u'<b><font color=red>ОШИБКА:</b> В справочнике отсутствует тип затраты для "%s"' % dbfFieldName)
                        continue
                    
                    if dbfFieldName not in self.baseServiceDbfRow.dbf.fieldNames:
                        self.log.append(u'<b><font color=red>ОШИБКА:</b> В загружаемом файле нет поля "%s"' % dbfFieldName)
                        continue
                    
                    self.totalPrice += forceDouble(self.baseServiceDbfRow[dbfFieldName])
                self.process(list(self.tariffList), self.updateTariffs)
            else:
                self.log.append(u'<b><font color=orange>Внимание:</b>'
                                u' Не найдено базовой услуги, соответвующей выбранному периоду')
            
        else:
            if not self.unitId:
                self.log.append(u'<b><font color=orange>Предупреждение:</b>'
                                u' Не задана единица учета медицинской помощи')
        
            self.process(self.dbfTariff, self.processTariff)
        


    def process(self, sourceList, stepFunction):
        self.progressBar.setMaximum(len(sourceList) - 1)
        for item in sourceList:
            QtGui.qApp.processEvents()
            if self.abort:
                self.reject()
                return
            self.progressBar.setValue(self.progressBar.value() + 1)
            QtGui.qApp.db.transaction()
            try:
                stepFunction(item)
                QtGui.qApp.db.commit()
            except:
                QtGui.qApp.db.rollback()
                QtGui.qApp.logCurrentException()
                raise
    
    
    def updateTariffs(self, currentTariff):
        db = QtGui.qApp.db
        serviceId = forceRef(currentTariff.value('service_id'))
        if not serviceId:
            self.log.append(u'<b><font color=orange>Предупреждение:</b> Тариф (%d) без услуги. Пропускаем.' % forceRef(currentTariff.value('id')))
            self.counter['skipped'] += 1
            return
        
        if not self.isLoadTariff(currentTariff):
            self.log.append(u'Тариф (%d) не попадает под условие текущего типа импорта. Пропускаем.' % forceRef(currentTariff.value('id')))
            self.counter['skipped'] += 1
            return

        totalUET = self.uetCache.setdefault(serviceId,
                                            forceDouble(db.translate('rbService', 'id', serviceId, 'adultUetDoctor')) +
                                            forceDouble(db.translate('rbService', 'id', serviceId, 'adultUetAverageMedWorker')))
        
        # tariffId = forceRef(currentTariff.value('id'))
        specialityId = forceRef(currentTariff.value('speciality_id'))
        tariffDate = forceDate(self.baseServiceDbfRow[self.fileFieldsInfo['begDateField'] if self.fileFieldsInfo.has_key('begDateField') else self.begDateField])
        updatedTariffIdList = self.addOrUpdateTariff(serviceId, 
                                                     specialityId,
                                                     tariffDate, 
                                                     self.baseServiceDbfRow, 
                                                     self.totalPrice * totalUET)
        
        for tariffId in updatedTariffIdList:
            self.updateCompositionExpense(tariffId, self.baseServiceDbfRow, totalPrice = self.totalPrice)
        
        
#        self.log.append(u'В тарифе {%d} изменена цена с "%.2f" на <b><font color=green>"%.2f"</b>' % (tariffId,
#                                                                                                    forceDouble(currentTariff.value('price')),
#                                                                                                    self.totalPrice  * totalUET))
#        currentTariff.setValue('price', toVariant(self.totalPrice  * totalUET))
#        self.counter['updated'] += 1
#        db.insertOrUpdate(self.tableContractTariff, currentTariff)
        
        
    

    def processTariff(self,  row):
        self.counter['processed'] += 1
        tariffDate = forceDate(row[self.fileFieldsInfo['begDateField'] if self.fileFieldsInfo.has_key('begDateField') else self.begDateField])
        
        fileServiceField = self.fileFieldsInfo['fileServiceField'] if self.fileFieldsInfo.has_key('fileServiceField') else self.fileServiceField
        serviceCode = forceStringEx(row[fileServiceField])
        if not serviceCode:
            self.log.append(u'<b><font color=orange>ОШИБКА:</b> Пустой код услуги')
            return
        
        if not self.isLoadTariff(row):
            self.log.append(u'Код услуги %s не соответствует выбранному типу тарифа' % serviceCode)
            self.counter['skipped'] += 1
            return
        
        serviceIdList = self.findServiceByCode(serviceCode)
        if not serviceIdList:
            self.log.append(u'<b><font color=orange>ОШИБКА:</b>'
                u' Услуга %s: не найдена' % serviceCode)
            self.counter['skipped'] += 1
            return
        
        strTariffDate = forceString(tariffDate.toString('dd.MM.yyyy'))
        if (self.begDate and tariffDate < self.begDate) or (self.endDate and tariffDate > self.endDate):
            self.log.append(u'Услуга: "%s". Дата "%s" вне периода загрузки.' % (serviceCode, strTariffDate))
            self.counter['skipped'] += 1
            return
        
        price = forceDouble(row[self.fileFieldsInfo.get('priceField', self.priceField)]) # float
        federalPriceField = self.fileFieldsInfo.get('federalPriceField', self.federalPriceField)
        federalPrice = forceDouble(row[federalPriceField]) if federalPriceField else None
        frag1StartField = self.fileFieldsInfo.get('frag1StartField', self.frag1StartField)
        frag1Start = forceInt(row[frag1StartField]) if frag1StartField else None
        frag1SumField = self.fileFieldsInfo.get('frag1SumField', self.frag1SumField)
        frag1Sum = forceDouble(row[frag1SumField]) if frag1SumField else None
        uetField = self.fileFieldsInfo.get('uetField', self.uetField)
        uet = forceDouble(row[uetField]) if uetField else None
        fileSpecialityField = self.fileFieldsInfo['fileSpecialityField'] if self.fileFieldsInfo.has_key('fileSpecialityField') else self.fileSpecialityField
        specialityCode = forceString(row[fileSpecialityField]) if fileSpecialityField else None # float

        if specialityCode is not None:
            specialityIdList = self.findSpecialityByCode(specialityCode)
        else:
            specialityIdList = []

        unitField = self.fileFieldsInfo.get('unitField', self.unitField)
        unitCode = forceString(row[unitField]) if unitField else None
        if unitCode is not None:
            unitIdList = self.findUnitByCode(unitCode)
        else:
            unitIdList = []

        ageField = self.fileFieldsInfo.get('ageField', self.ageField)
        age = None if ageField is None else forceStringEx(row[ageField])
        if age:
            try:
                parseAgeSelector(age)
            except ValueError:
                age = None

        if not specialityIdList:
            if fileSpecialityField:
                self.log.append(u'<b><font color=orange>ОШИБКА:</b>'
                                u' Специальность с кодом "%s" не найдена' % specialityCode)
                self.counter['skipped'] += 1
                return
            else:
                specialityIdList = [None]

        if self.fillUET:
            self.updateUetMapping(serviceIdList)
        
        for serviceId in serviceIdList:
            for specialityId in specialityIdList:
                self.log.append(u'----Услуга: "%s". Дата "%s". Специальность: "%s". Тариф: <b><font color=green>"%.2f"</b>----' % (serviceCode, strTariffDate, specialityCode, price))
                updatedTariffIdList = self.addOrUpdateTariff(serviceId, 
                                                             specialityId, 
                                                             tariffDate, 
                                                             row, 
                                                             price,
                                                             federalPrice=federalPrice,
                                                             uet=uet,
                                                             frag1Start=frag1Start,
                                                             frag1Sum=frag1Sum,
                                                             unitIdList = unitIdList,
                                                             age = age)
        
                for tariffId in updatedTariffIdList:
                    self.updateCompositionExpense(tariffId, row, totalPrice = price)
                    self.log.append(u'Обновлены статьи затрат для тарифа по услуге %s на дату %s' % (forceString(row[fileServiceField]),
                                                                                                     tariffDate.toString('dd.MM.yyyy')))
            
                self.log.append(u'-----------------------------------------------------------------')
        
    
    def addOrUpdateTariff(self, serviceId, specialityId, tariffDate, tariffDbfRecord, price,
                          federalPrice=None, uet=None, frag1Start=None, frag1Sum=None, unitIdList=None, age=None):
        serviceTariffList = self.tariffIdxByServiceAndSpecialityId.setdefault((serviceId, specialityId), [])
        
        serviceTariffIndex = 0
        needAdd = True

        if age is None:
            age = self.defaultAge

        fileServiceField = self.fileFieldsInfo['fileServiceField'] if self.fileFieldsInfo.has_key('fileServiceField') else self.fileServiceField
        endDateField = self.fileFieldsInfo['endDateField'] if self.fileFieldsInfo.has_key('endDateField') else self.endDateField

        totalUet = self.mapServiceIdToUet.get(serviceId, (0.0, 0.0, 0.0, 0.0))
        defaultUet = totalUet[0] or totalUet[1] # если указан детский УЕТ и не указан взрослый, используем детский

        if not endDateField is None:
            endDate = forceDate(tariffDbfRecord[endDateField])
        else:
            if QtGui.qApp.defaultKLADR()[:2] == '23':
                # i2669. Для Краснодарского Края дата окончания должна быть пустой
                endDate = QtCore.QDate()
            else:
                endDate = QtCore.QDate(QtCore.QDate.currentDate().year(), 12, 31)
        updatedTariffIdList = []
        tariff = None
        for serviceTariffIndex, mainTariffIndex in enumerate(serviceTariffList):
            tariff = self.tariffList[mainTariffIndex]
            # Если для текущего типа импорта установлен фильтр по возрасту, то пропускать все тарифы, у которых возраст не соотв. фильтру..

            if age and forceStringEx(tariff.value('age')) != age:
                self.log.append(u'Фильтр по возрасту для тарифа (%s) и для типа импорта (%s) отличаются' % (forceStringEx(tariff.value('age')),
                                                                                                            age))
                continue
            if self.distinctEventType and self.eventTypeId != forceRef(tariff.value('eventType_id')):
                self.log.append(u'Фильтр по типу события для тарифа и для типа импорта отличаются')
                continue

            tariffBegDate = forceDate(tariff.value('begDate'))
            # Если дата текущего тарифа больше, чем дата самого позднего тарифа в договоре
            if tariffDate > tariffBegDate:
                if serviceTariffIndex == 0: # Если на данном шаге цикла мы находимся на самом позднем/новом тарифе (т.е. первый по порядку)
                    # То обновляем дату окончания этого тарифа на дату начала добавляемого
                    tariff.setValue('endDate', toVariant(tariffDate.addDays(-1)))
                    QtGui.qApp.db.insertOrUpdate(self.tableContractTariff, tariff)
                # выходим из цикла и переходим к добавлению нового тарифа, так как needAdd не переведен в False
                break
            # Если дата текущего тарифа равна дате существующего тарифа, то считать эти тарифы совпадающими
            elif tariffDate == tariffBegDate:
                needAdd = False
                
                oldPrice = forceDouble(tariff.value('price'))
                oldAmount = forceDouble(tariff.value('amount'))
                oldEndDate = forceDate(tariff.value('endDate'))
                self.log.append(u'Найден совпадающий тариф %s - %s (Цена: %0.2f, Кол-во: %d).' % (tariffDate.toString('dd.MM.yy'),
                                                                                                  oldEndDate.toString('dd.MM.yy'),
                                                                                                  oldPrice, 
                                                                                                  oldAmount))
                # if abs(oldPrice - price) < self.precision and abs(oldAmount - self.amount) < self.precision:
                #     self.log.append(u'Количество и цена совпадают, пропускаем.')
                #     continue
                
                answer = None
                if self.duplicateBehavior.checkedId() == 2: #спросить у пользователя
                    self.log.append(u'Запрос действий у пользователя.')
                    answer = QtGui.QMessageBox.question(self, u'Совпадающий тариф',
                                                        u'Услуга "%s",\n'
                                                        u'Количество: %.2f, новое количество %.2f\n'
                                                        u'Тариф: %.2f, новый %.2f\n'
                                                        u'Обновить?' %(forceString(tariffDbfRecord[fileServiceField]), 
                                                                       oldAmount, self.amount, 
                                                                       oldPrice, price),
                                                        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                                        QtGui.QMessageBox.No)
                    self.log.append(u'Выбор пользователя %s' % (u'обновить' if answer == QtGui.QMessageBox.Yes else u'пропустить'))
                
                if answer == QtGui.QMessageBox.No or self.duplicateBehavior.checkedId() == 1: #пропустить
                    self.log.append(u'Пропускаем.')
                    continue

                serviceCode = forceString(tariffDbfRecord[fileServiceField])
                tableService = QtGui.qApp.db.table('rbService')
                serviceList = QtGui.qApp.db.getIdList(tableService, 'id', tableService['code'].eq(serviceCode))
                if len(serviceList) > 1:
                    # i2669. В rbService могут быть услуги c одинаковым rbService.code
                    # Чтобы избежать дублирования, пропускаем
                    self.log.append(u'"%s" не обновлена, услуга дублируется по коду' % serviceCode)
                    continue

                self.log.append(u'Обновляем тариф {%d}. (Цена: %.2f на %.2f, Дата окончания %s на %s)' % (forceRef(tariff.value('id')),
                                                                                                          oldPrice, 
                                                                                                          price,
                                                                                                          oldEndDate.toString('dd.MM.yy'),
                                                                                                          endDate.toString('dd.MM.yy')))

                tariff.setValue('price', toVariant(price))
                tariff.setValue('endDate', toVariant(endDate))
                
                tariff.setValue('tariffType', toVariant(self.tariffType))
                tariff.setValue('amount',  toVariant(self.amount))
                tariff.setValue('unit_id',  toVariant(unitIdList[0] if unitIdList else self.unitId))
                if age:
                    tariff.setValue('age',  toVariant(age))
                if federalPrice:
                    tariff.setValue('federalPrice', toVariant(federalPrice))
                if uet is not None:
                    tariff.setValue('uet', toVariant(uet))
                elif self.fillUET:
                    tariff.setValue('uet', toVariant(defaultUet))
                tariff.setValue('speciality_id', toVariant(specialityId))
                if self.eventTypeId and not forceRef(tariff.value('eventType_id')):
                    tariff.setValue('eventType_id', toVariant(self.eventTypeId))

                if not frag1Start is None:
                    tariff.setValue('frag1Start', toVariant(frag1Start))
                    tariff.setValue('frag1Sum', toVariant(frag1Sum))
                elif self.isUpdateFrag1Start:
                    serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'code')) #TODO: atronah: fix this shit
                    frag1Start = forceInt(QtGui.qApp.db.translate('mes.MES', 'code', serviceCode, 'maxDuration'))
                    tariff.setValue('frag1Start', toVariant(frag1Start))
                    tariff.setValue('frag1Sum', toVariant(frag1Start * price))

                QtGui.qApp.db.insertOrUpdate(self.tableContractTariff, tariff)
                updatedTariffIdList.append(forceRef(tariff.value('id')))
                self.counter['updated'] += 1
                break
            else:
                endDate = tariffBegDate.addDays(-1) if endDateField is None else forceDate(tariffDbfRecord[endDateField])


        if needAdd:
            serviceCode = forceString(tariffDbfRecord[fileServiceField])
            tableService = QtGui.qApp.db.table('rbService')
            serviceList = QtGui.qApp.db.getIdList(tableService, 'id', tableService['code'].eq(serviceCode))
            if len(serviceList) > 1:
                # i2669. В rbService могут быть услуги c одинаковым rbService.code
                # Чтобы избежать дублирования, пропускаем
                self.log.append(u'"%s" не добавлена, услуга дублируется по коду' % serviceCode)
            else:
                if tariffDate < endDate.addDays(1) and serviceTariffIndex != 0:
                    serviceTariffIndex += 1
                self.log.append(u'Добавляем тариф.')

                newTariff = self.tableContractTariff.newRecord()
                newTariff.setValue('master_id',  toVariant(self.contractId))
                newTariff.setValue('tariffType', toVariant(self.tariffType))
                newTariff.setValue('service_id', toVariant(serviceId))
                newTariff.setValue('sex', toVariant(''))
                newTariff.setValue('age', toVariant(age))
                newTariff.setValue('unit_id',  toVariant(unitIdList[0] if unitIdList else self.unitId))
                newTariff.setValue('amount',  toVariant(self.amount))
                newTariff.setValue('limit',  toVariant(0.0))
                newTariff.setValue('speciality_id', toVariant(specialityId))
                if frag1Start is not None:
                    newTariff.setValue('frag1Start', toVariant(frag1Start))
                    newTariff.setValue('frag1Sum', toVariant(frag1Sum))
                elif self.isUpdateFrag1Start:
                    serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'code')) #TODO: atronah: fix this shit
                    frag1Start = forceInt(QtGui.qApp.db.translate('mes.MES', 'code', serviceCode, 'maxDuration'))
                    newTariff.setValue('frag1Start', toVariant(frag1Start))
                    newTariff.setValue('frag1Sum', toVariant(frag1Start * price))
                if self.eventTypeId:
                    newTariff.setValue('eventType_id', toVariant(self.eventTypeId))

                newTariff.setValue('price', toVariant(price))
                newTariff.setValue('begDate', toVariant(tariffDate))
                newTariff.setValue('endDate', toVariant(endDate))
                if federalPrice is not None:
                    newTariff.setValue('federalPrice', toVariant(federalPrice))
                if uet is not None:
                    newTariff.setValue('uet', toVariant(uet))
                if self.fillUET:
                    newTariff.setValue('uet', toVariant(defaultUet))

                newTariffId = QtGui.qApp.db.insertOrUpdate(self.tableContractTariff, newTariff)
                #индекс тарифа в основном списке тарифов
                mainTariffIndex = len(self.tariffList)
                self.tariffList.append(newTariff)
                serviceTariffList.insert(serviceTariffIndex, mainTariffIndex)
                self.counter['added'] += 1
                updatedTariffIdList.append(newTariffId)
        
        return updatedTariffIdList


    def updateCompositionExpense(self, masterId, tariffDbfRecord, totalPrice = None):
        db = QtGui.qApp.db
        tableExpense = db.table('Contract_CompositionExpense')
        if not masterId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b> Попытка записать статьи затрат без указания id тарифа.')
            return False
        
        
        price = totalPrice or forceDouble(tariffDbfRecord[self.fileFieldsInfo['priceField'] if self.fileFieldsInfo.has_key('priceField') else self.priceField])
        
        updatedExpenseId = []
        for dbfFieldName, expenceServiceItemId in self.mapCompositionExpenseFieldNameToId.items():
            if not expenceServiceItemId:
                self.log.append(u'<b><font color=red>ОШИБКА:</b> В справочнике отсутствует тип затраты для "%s"' % dbfFieldName)
                continue
            
            if dbfFieldName not in tariffDbfRecord.dbf.fieldNames:
                self.log.append(u'<b><font color=red>ОШИБКА:</b> В загружаемом файле нет поля "%s"' % dbfFieldName)
                continue
        

            expenceInPercent = 100 * forceDouble(tariffDbfRecord[dbfFieldName]) / price if price > self.precision else 0.0
            
            
            expenseRecord = db.getRecordEx(tableExpense, '*', [tableExpense['master_id'].eq(masterId),
                                                               tableExpense['rbTable_id'].eq(expenceServiceItemId)])
            if not expenseRecord:
                expenseRecord = tableExpense.newRecord()
                expenseRecord.setValue('master_id', toVariant(masterId))
                expenseRecord.setValue('rbTable_id', toVariant(expenceServiceItemId))
            expenseRecord.setValue('percent', toVariant(expenceInPercent))
            expenseId = db.insertOrUpdate(tableExpense, expenseRecord)
            updatedExpenseId.append(expenseId)
        
        
        # Обнуление всех остальных статей затрат
        db.updateRecords(tableExpense, 
                         expr = 'percent = 0.0',
                         where = [tableExpense['master_id'].eq(masterId),
                                 tableExpense['id'].notInlist(updatedExpenseId)])            
        
        return True
    
    
    ## 
    # @param dataType: тип данных CImportTariffs.DataType
    def findIdByCode(self, code, dataType):
        if dataType == CImportTariffs.DataType.Service:
            cache = self.serviceCache
            dbRule = self.fileFieldsInfo['dbServiceFieldRule'] if self.fileFieldsInfo.has_key('dbServiceFieldRule') else self.dbServiceFieldRule
        elif dataType == CImportTariffs.DataType.Speciality:
            cache = self.specialityCache
            dbRule = self.fileFieldsInfo['dbSpecialityFieldRule'] if self.fileFieldsInfo.has_key('dbSpecialityFieldRule') else self.dbSpecialityFieldRule
        else:
            cache = self.unitCache
            dbRule = self.fileFieldsInfo.get('dbUnitFieldRule', self.dbUnitFieldRule)
        if not cache.has_key(code):
            result = [toVariant(code)]
            for tableName, compareFieldName, resultFieldName in dbRule:
                table = QtGui.qApp.db.forceTable(tableName)
                result = [record.value(0) for record in QtGui.qApp.db.getRecordList(table = table, 
                                                                                    cols = resultFieldName, 
                                                                                    where = table[compareFieldName].inlist(result))]
            result = [forceRef(item) for item in result]
            if result:
                cache[code] = result
        return cache.get(code, [])
    
    
    def findServiceByCode(self, code):
        return self.findIdByCode(code, dataType = CImportTariffs.DataType.Service)
    

    def findSpecialityByCode(self, code):
        return self.findIdByCode(code, dataType = CImportTariffs.DataType.Speciality)

    def findUnitByCode(self, code):
        return self.findIdByCode(code, dataType = CImportTariffs.DataType.Unit)

    def updateUetMapping(self, serviceIdList):
        newServices = set(serviceIdList).difference(set(self.mapServiceIdToUet))

        db = QtGui.qApp.db
        tblService = db.table('rbService')
        records = db.getRecordList(tblService,
                                   [tblService['id'],
                                    tblService['adultUetDoctor'],
                                    tblService['childUetDoctor'],
                                    tblService['adultUetAverageMedWorker'],
                                    tblService['childUetAverageMedWorker']],
                                   [tblService['id'].inlist(newServices)])
        for record in records:
            self.mapServiceIdToUet[forceRef(record.value('id'))] = (forceDouble(record.value('adultUetDoctor')),
                                                    forceDouble(record.value('childUetDoctor')),
                                                    forceDouble(record.value('adultUetAverageMedWorker')),
                                                    forceDouble(record.value('childUetAverageMedWorker')))


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            dbfFileName = forceStringEx(self.edtFileName.text())
            dbfTariff = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfTariff)))
            dbfTariff.close()
        self.checkName()
    
    
    @QtCore.pyqtSlot(int)
    def onImportTypeChanged(self, idx):
        importTypeInfo = self.importTypeList[idx]
        
        self.gbDublicates.setEnabled(not importTypeInfo['isUpdateTariffViaBaseService'])
        self.gbTariffParameters.setEnabled(not importTypeInfo['isUpdateTariffViaBaseService'])
            
        if not importTypeInfo['isUpdateTariffViaBaseService']:
            self.lblEventType.setEnabled(importTypeInfo['fillEventType'])
            self.cmbEventType.setEnabled(importTypeInfo['fillEventType'])
            if importTypeInfo['unitCode']:
                self.cmbMedicalAidUnit.setCode(importTypeInfo['unitCode'])
            else:
                self.cmbMedicalAidUnit.setValue(None)
            
            self.cmbTariffType.setCurrentIndex(importTypeInfo['defaultTariffType'] or 0)

            self.chkFillUET.setChecked(importTypeInfo['isFillUET'])

        self.teInfo.clear()
        self.teInfo.setHtml(self.currentImportTypeHtmlInfo())

    def setUnitVisible(self, state):
        self.cmbMedicalAidUnit.setVisible(state)
        self.lblMedicalAidUnit.setVisible(state)