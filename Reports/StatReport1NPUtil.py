# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtGui


ageSexRows = [
    (u'до 35 лет',         u'01'),
    (u'из них:\n- мужчины',u'01.1'),
    (u'- женщины',         u'01.2'),
    (u'от 35 до 55 лет',   u'02'),
    (u'из них:\n- мужчины',u'02.1'),
    (u'- женщины',         u'02.2'),
    (u'старше 55 лет',     u'03'),
    (u'из них:\n- мужчины',u'03.1'),
    (u'- женщины',         u'03.2'),
    (u'Всего',             u'04'),
    (u'из них:\n- мужчины',u'04.1'),
    (u'- женщины',         u'04.2'),
]

def dispatchAgeSex(age, sex):
    result = []
    if age < 35:
        if sex == 1:
            result = [0, 1, 9, 10]
        elif sex == 2:
            result = [0, 2, 9, 11]
    elif age <= 55:
        if sex == 1:
            result = [3, 4, 9, 10]
        elif sex == 2:
            result = [3, 5, 9, 11]
    else:
        if sex == 1:
            result = [6, 7, 9, 10]
        elif sex == 2:
            result = [6, 8, 9, 11]
    return result


def havePermanentAttach(date):
# существует постоянное прикрепление к тек. ЛПУ действующее на заданную дату
# и не перекрытое другим постоянным прикреплением (выбытием или смертью)

    stmt = """
EXISTS (SELECT CA.id FROM ClientAttach AS CA
 WHERE  CA.client_id = Client.id
   AND  CA.deleted = 0
   AND  CA.LPU_id = %d
   AND  CA.attachType_id IN (SELECT id FROM rbAttachType WHERE `temporary`=0 AND `outcome`=0)
   AND  CA.begDate <= %s
   AND  (CA.endDate >= %s OR CA.endDate IS NULL)
   AND  CA.id IN (SELECT MAX(CA2.id) FROM ClientAttach AS CA2
                 WHERE CA2.client_id = Client.id
                 AND   CA2.deleted = 0
                 AND   CA2.attachType_id IN (SELECT id FROM rbAttachType WHERE `temporary`=0)
                 AND   CA2.begDate <= %s
                 AND  (CA2.endDate >= %s OR CA2.endDate IS NULL)
                )
)"""
    d = QtGui.qApp.db.formatDate(date)
    return stmt % ( QtGui.qApp.currentOrgId(), d, d, d, d )