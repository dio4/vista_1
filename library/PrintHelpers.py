# -*- coding: utf-8 -*-
u"""
В этом модуле описаны функции, которые будут доступны через шаблоны печати. Такие функции
должны быть добавлены в список __all__.
"""
import hashlib


__all__ = ['md5']


def md5(src):
    return hashlib.md5(unicode(src)).hexdigest()
