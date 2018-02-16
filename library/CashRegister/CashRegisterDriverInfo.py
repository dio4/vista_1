# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

"""
Created on 26.09.2013

@author: atronah
"""

class CCashRegisterDriverInfo:
    progID = u'AddIn.FPrnM45'
    
    
    # Информация о поддерживаемых режимах работы
    class Mode:
        registration = 1
        xReport = 2
        zReport = 3
        
        
        titles = {0 : u'Выбор',
                  1 : u'Регистрация',
                  2 : u'X-отчеты',
                  3 : u'Z-отчеты',
                  4 : u'Программирование',
                  5 : u'Доступ к ФП',
                  6 : u'Доступ к ЭКЛЗ',
                  7 : u'Дополнительный'
                 }


        @staticmethod
        def title(mode):
            return CCashRegisterDriverInfo.Mode.titles.get(mode, u'Неизвестный режим {%s}' % mode)
    
    
    # Информация о поддерживаемых типах чеков
    class CheckType:
        sale = 1
        returnSale = 2
        annulateSale = 3
        buy = 4
        returnBuy = 5
        annulateBuy = 6
        
        titles = {sale : u'Продажа',
                  returnSale : u'Возврат продажи',
                  annulateSale: u'Аннулирование продажи',
                  buy : u'Покупка',
                  returnBuy : u'возврат покупки',
                  annulateBuy : u'Аннулирование покупки'}
        
        @staticmethod
        def title(checkType):
            return CCashRegisterDriverInfo.CheckType.titles.get(checkType, u'Неизвестный тип чека {%s}' % checkType)

    
    # Информация о поддерживаемых типах отчетов
    class ReportType: 
        titles = {
                  1 : u'Суточный отчет с гашением.',
                  2 : u'Суточный отчет без гашения'
                  }
        
        @staticmethod
        def title(reportType):
            return CCashRegisterDriverInfo.ReportType.titles.get(reportType, u'Неизвестный тип отчета {%s}' % reportType)
    
    #Информация о типе скидки
    class DiscountType:
        absolute = currency = 0
        percent = 1 
    
    # Информация о моделях ККМ
    class Model:
        #Список моделей с автоматически открывающейся сменой (при печате первого чека)
        AutoOpennedSessionModelList = [25, 28, 107, 110, 113]

        titles = {0 : u'ЭЛВЕС-МИКРО-Ф',
                  13 : u'Триум-Ф',
                  14 : u'ФЕЛИКС-Р Ф',
                  15 : u'ФЕЛИКС-02К / ЕНВД',
                  16 : u'МЕРКУРИЙ-140',
                  17 : u'МЕРКУРИЙ-114.1Ф',
                  18 : u'ШТРИХ-ФР-Ф',
                  19 : u'ЭЛВЕС-МИНИ-ФР-Ф',
                  20 : u'ТОРНАДО',
                  23 : u'ТОРНАДО-К',
                  24 : u'ФЕЛИКС-РК / ЕНВД',
                  25 : u'ШТРИХ-ФР-К',
                  26 : u'ЭЛВЕС-ФР-К',
                  27 : u'ФЕЛИКС-3СК',
                  28 : u'ШТРИХ-МИНИ-ФР-К',
                  30 : u'FPrint-02K / ЕНВД',
                  31 : u'FPrint-03K / ЕНВД',
                  32 : u'FPrint-88K / ЕНВД',
                  33 : u'BIXOLON-01K',
                  35 : u'FPrint-5200K / ЕНВД',
                  41 : u'PayVKP-80K',
                  42 : u'Аура-01ФР-KZ',
                  43 : u'PayVKP-80KZ',
                  45 : u'PayPPU-700K',
                  46 : u'PayCTS-2000K',
                  47 : u'FPrint-55K / ЕНВД',
                  50 : u'Wincor Nixdorf TH-230K',
                  51 : u'FPrint-11K ПТК / ЕНВД',
                  52 : u'FPrint-22K / ЕНВД',
                  101 : u'POSPrint FP410K',
                  102 : u'МSTAR-Ф',
                  103 : u'Мария-301 МТМ',
                  104 : u'ПРИМ-88ТК',
                  105 : u'ПРИМ-08ТК',
                  106 : u'СП101ФР-К',
                  107 : u'ШТРИХ-КОМБО-ФР-К',
                  108 : u'ПРИМ-07К',
                  109 : u'МИНИ-ФП6',
                  110 : u'ШТРИХ-М-ФР-К',
                  111 : u'MSTAR-TK.1',
                  113 : u'ШТРИХ-LIGHT-ФР-К',
                  114 : u'ПИРИТ ФР01К',
                  115 : u'NCR-001K',
                  116 : u'IKC-E260T',
                  118 : u'ШТРИХ-ФР-Ф (БЕЛАРУСЬ)'
                  }
        
        @staticmethod
        def title(model):
            return CCashRegisterDriverInfo.Model.titles.get(model, u'Неизвестная модель {%s}' % model)