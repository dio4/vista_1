# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 26.09.2013

@author: atronah

Модуль, отвечающий за работу с Контрольно-кассовой машиной (ККМ или касса)
через драйвер фирмы ATOL (www.atol.ru) v8.x

CashRegisterDriverInfo      - Содержит класс с информацией о драйвере (список моделей и их кодов, типы и их наименования и т.п.).
CashRegisterEmulator        - Содержит класс для эмуляции работы драйвера средствами python для тестирования модуля.
CashRegisterEngine          - Содержит основноё функционал по работе с ККМ.
CashRegisterOperationInfo   - Содержит класс для хранения и предоставления информации о проводимых операциях по кассе,
                                а также класс пользовательского интерфейса для уточнения этой информации у пользователя.
CashRegisterOperationWindow - Содержит класс пользовательского интерфейса для модуля.
CashRegisterItemModel       - Содержит класс для хранения информации об элементах чека, и класс, определяющий модель для этих элементов.
ECRLogger                   - Содержит класс по загрузке из базы данных и записи в нее данных о проведенных по кассе операциях.
"""
