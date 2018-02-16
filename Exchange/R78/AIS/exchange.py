#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

def main():
    from PyQt4 import QtCore
    from hospital import Exchange
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    if len(sys.argv) == 2:
        if str(sys.argv[1]) == '-b':
            sender = Exchange()
            sender.owner_hospital_vacancy_upload()
            sender.owner_selection_commission_timetable_period_upload()
        elif str(sys.argv[1]) == '-h':
            sender = Exchange()
            sender.sendHospital()
    else:
        print 'Enter plz key: \n -b = send Beds package \n -h = send Hospitalisations package'

if __name__ == '__main__':
    main()