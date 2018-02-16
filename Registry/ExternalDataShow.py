# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2012 SAMSON Group. All rights reserved.
##
#############################################################################
##
## Это программа является свободным программным обеспечением.
## Вы можете использовать, распространять и/или модифицировать её согласно
## условиям GNU GPL версии 3 или любой более поздней версии.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import *

from Ui_ExternalDataShowDialog import Ui_ExternalDataShowDialog


class CExternalDataShow(QtGui.QDialog, Ui_ExternalDataShowDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)


class CUekDataShow(CExternalDataShow):

    def __init__(self, parent):
        CExternalDataShow.__init__(self, parent)
        self.setWindowTitle(u'Информация с УЭК')

    def exec_(self, cardReader=None):
        db = QtGui.qApp.db
        insurerName = db.getRecordEx('Organisation', 'shortName',
                                     'deleted = 0 AND isInsurer = 1 AND'
                                     ' OGRN = "%s" AND OKATO = "%s"' % (cardReader.insurerOGRN,
                                                                        cardReader.insurerOKATO))
        insurerName = '' if not insurerName else forceString(insurerName.value('shortName'))
        documentName = '' if not cardReader.documentType else forceString(db.translate('rbDocumentType', 'federalCode',
                                                                                       cardReader.documentType, 'name'))
        self.tbCardData.setText(
            u'''
            <center><b>Персональные данные</b></center><br>
            <b>Фамилия:</b> %s<br>
            <b>Имя:</b> %s<br>
            <b>Отчество:</b> %s<br>
            <b>Пол:</b> %s<br>
            <b>Дата рождения:</b> %s<br>
            <b>Место рождения:</b> %s<br>
            <b>СНИЛС:</b> %s<br>
            <center><b>Полис ОМС</b></center><br>
            <b>Номер:</b> %s<br>
            <b>Дата начала действия:</b> %s<br>
            <b>ОГРН СМО:</b> %s<br>
            <b>ОКАТО СМО:</b> %s<br>
            <b>Наименование СМО:</b> %s<br>
            <center><b>Документ, удостоверяющий личность</b></center><br>
            <b>Тип:</b> %s<br>
            <b>Серия:</b> %s<br>
            <b>Номер:</b> %s<br>
            <b>Дата выдачи:</b> %s<br>
            <b>Кем выдано:</b> %s<br>
            ''' % (cardReader.lastName,
                   cardReader.firstName,
                   cardReader.patrName,
                   cardReader.sex,
                   cardReader.birthDate,
                   cardReader.birthPlace,
                   cardReader.SNILS,
                   cardReader.policyNumber,
                   cardReader.policyBegDate,
                   cardReader.insurerOGRN,
                   cardReader.insurerOKATO,
                   u'не найдено' if not insurerName else insurerName,
                   u'не найдено' if not documentName and cardReader.documentType else documentName,
                   cardReader.documentSerial,
                   cardReader.documentNumber,
                   cardReader.documentDate,
                   cardReader.documentOrigin)
        )
        return QtGui.QDialog.exec_(self)


class CErzDataShow(CExternalDataShow):

    def __init__(self, parent):
        CExternalDataShow.__init__(self, parent)
        self.setWindowTitle(u'Информация с ЕРЗ')

    def exec_(self, response=None):
        db = QtGui.qApp.db
        insurerName = '' if not response['policyKSMO'] else \
            db.getRecordEx('Organisation', 'shortName', 'deleted = 0 AND isInsurer = 1'
                                                        ' AND infisCode = "%s"' % response['policyKSMO'])
        if not insurerName:
            insurerName = db.getRecordEx('Organisation', 'shortName',
                                         'deleted = 0 AND isInsurer = 1 AND head_id IS NULL'
                                         ' AND OGRN = "%s" AND OKATO = "%s"' % (response['policyOGRN'],
                                                                                response['policyOKATO']))
        insurerName = '' if not insurerName else forceString(insurerName.value('shortName'))
        policyKindName = '' if not response['policyType'] else forceString(db.translate('rbPolicyKind', 'regionalCode',
                                                                                        response['policyType'], 'name'))
        self.tbCardData.setText(
            u'''
            <center><b>Персональные данные</b></center><br>
            <b>Фамилия:</b> %s<br>
            <b>Имя:</b> %s<br>
            <b>Отчество:</b> %s<br>
            <b>Пол:</b> %s<br>
            <b>Дата рождения:</b> %s<br>
            <center><b>Полис ОМС</b></center><br>
            <b>Тип:</b> %s<br>
            <b>Серия:</b> %s<br>
            <b>Номер:</b> %s<br>
            <b>Дата начала действия:</b> %s<br>
            <b>Дата окончания действия:</b> %s<br>
            <b>Код СМО:</b> %s<br>
            <b>ОГРН СМО:</b> %s<br>
            <b>ОКАТО СМО:</b> %s<br>
            <b>Наименование СМО:</b> %s<br>
            ''' % (nameCase(response['lastName']),
                   nameCase(response['firstName']),
                   nameCase(response['patrName']),
                   response['sex'],
                   response['birthDate'].toString('dd.MM.yyyy'),
                   u'не найдено' if not policyKindName else policyKindName,
                   response['policySerial'],
                   response['policyNumber'],
                   response['policyBegDate'].toString('dd.MM.yyyy'),
                   response['policyEndDate'].toString('dd.MM.yyyy'),
                   response['policyKSMO'],
                   response['policyOGRN'],
                   response['policyOKATO'],
                   u'не найдено' if not insurerName else insurerName)
        )
        return QtGui.QDialog.exec_(self)