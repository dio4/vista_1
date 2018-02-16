# -*- coding: utf-8 -*-

from library.ListModel import CListModel

serviceTypeNames = [
    u'-',
    u'Прочие',
    u'Первичный осмотр',
    u'Повторный осмотр',
    u'Процедура/манипуляция',
    u'Операция',
    u'Исследование',
    u'Лечение',
    u'Расходники',
    u'Оплата палат',
    u'Реанимация',
    u'Профиль',
    u'Лабораторные исследования',
    u'Функциональная диагностика',
    u'Эпикриз',
    u'Анестезия'
]


class CServiceTypeModel(CListModel):
    def __init__(self, start, end=None):
        CListModel.__init__(self, serviceTypeNames[start:] if (end is None) else serviceTypeNames[start:end], serviceTypeNames)

