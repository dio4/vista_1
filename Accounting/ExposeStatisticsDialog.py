# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2016 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui
from library.DialogBase import CDialogBase
from Ui_ExposeStatisticsDialog import Ui_ExposeStatisticsDialog
from library.Utils import forceString


class CExposeStatisticsDialog(CDialogBase, Ui_ExposeStatisticsDialog):

    def __init__(self, parent, accountIdList):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.accountIdList = accountIdList

    def refreshStatistics(self):
        db = QtGui.qApp.db
        tableAccount = db.table('Account')
        tableAccountItem = db.table('Account_Item')
        statsText = u''

        for accountId in self.accountIdList:
            accountRecord = db.getRecord(tableAccount, '*', accountId)
            casesCount = db.getDistinctCount(tableAccountItem, 'event_id', where=tableAccountItem['master_id'].eq(accountId))
            mesCount = db.getCount(table=None, stmt=u'''
                SELECT
                    COUNT(DISTINCT Action.id)
                FROM
                    Event
                    INNER JOIN Account_Item ON Event.id = Account_Item.event_id
                    INNER JOIN Action ON Action.event_id = Event.id
                    INNER JOIN ActionType ON Action.actionType_id = ActionType.id
                WHERE
                    Account_Item.master_id = %s
                    AND ActionType.flatCode like 'moving%%'
                    AND Action.mes_id is not null;
            ''' % forceString(accountId))
            serviceCount = db.getCount(tableAccountItem, '*', where=tableAccountItem['master_id'].eq(accountId))
            statsText += u'Счет ' + forceString(accountRecord.value('number')) + u'\n'

            statsText += u'Всего случаев: ' + forceString(casesCount) + u'\n'
            statsText += u'Всего стандартов выставлено (из действия движение): ' + forceString(mesCount) + u'\n'
            statsText += u'Всего услуг выставлено: ' + forceString(serviceCount) + u'\n'

            statsText += u'\n'
            statsText += u'################\n'

        self.txtStats.setText(statsText)
