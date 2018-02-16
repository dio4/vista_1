# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from library.InDocTable import CInDocTableModel, CDateInDocTableCol, CFloatInDocTableCol, CCalculatedInDocTableCol


'''
Created on 11.04.2014

@author: atronah
'''


class CClientAntrophometricModel(CInDocTableModel):
    def __init__(self, parent = None):
        super(CClientAntrophometricModel, self).__init__(u'ClientAnthropometric',
                                                         u'id',
                                                         u'client_id',
                                                         parent)
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 50))
        #atronah: возможно лучше текстом, так как CIntInDocTableCol вроде не допускает пустого значения 
        self.addCol(CFloatInDocTableCol(u'Рост, см', 'height', 15, min = 30, max = 290, precision = 1))
        self.addCol(CFloatInDocTableCol(u'Вес, кг', 'weight', 15, min = 0.200, max = 700, precision = 3))
        self.addCol(CFloatInDocTableCol(u'Об. талии, см', 'waist', 15, min = 30, max = 500, precision = 1))
        self.addCol(CFloatInDocTableCol(u'Об. груди, см', 'bust', 15, min = 30, max = 500, precision = 1))
        self.addCol(CCalculatedInDocTableCol(u'Индекс массы тела', 
                                             'height', 
                                             50, 
                                             additionalFieldList = ['weight'],
                                             calculateFunc = lambda h, w: round(w.toDouble()[0] / (max(h.toDouble()[0] / 100, 0.001) ** 2), 1)
                                             ))
        
