# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.DialogBase     import CDialogBase

from Ui_TemplateDialog      import Ui_ResourceTemplateDialog


class CTemplateDialog(CDialogBase, Ui_ResourceTemplateDialog):
    def __init__(self, parent, orgStructureId = None, currentJobTypeId = None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self._currentJobTypeId = currentJobTypeId
        # today = QtCore.QDate.currentDate()
#        self.edtBegDate.setDateRange(today.addMonths(-1), today.addMonths(13))
#        self.edtEndDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtBegDate.setFocus(QtCore.Qt.OtherFocusReason)
        queueTypeFilter = (u'orgStructure_id = %s' % orgStructureId) if orgStructureId else u''
        self.cmbEQueueType.setTable(u'rbEQueueType', filter = queueTypeFilter)


    def setDateRange(self, begDate, endDate):
        self.edtBegDate.setDateRange(begDate, endDate)
        self.edtEndDate.setDateRange(begDate, endDate)
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)


    def setDefaults(self, begTime, endTime, quantity, eQueueTypeId = None):
            for widget in [self.edtTimeRange1, self.edtTimeRange2, self.edtTimeRange3,
                           self.edtTimeRange4, self.edtTimeRange5, self.edtTimeRange6, self.edtTimeRange7]:
                widget.setTimeRange((begTime, endTime))
            for widget in [self.edtQuantity1, self.edtQuantity2, self.edtQuantity3,
                           self.edtQuantity4, self.edtQuantity5, self.edtQuantity6, self.edtQuantity7]:
                widget.setValue(quantity)
            for widget in [self.chkOvertime1, self.chkOvertime2, self.chkOvertime3,
                           self.chkOvertime4, self.chkOvertime5, self.chkOvertime6, self.chkOvertime7]:
                widget.setChecked(False)
            for widget in [self.dsbLimitSuperviseUnit1, self.dsbLimitSuperviseUnit2, self.dsbLimitSuperviseUnit3,
                           self.dsbLimitSuperviseUnit4, self.dsbLimitSuperviseUnit5, self.dsbLimitSuperviseUnit6, self.dsbLimitSuperviseUnit7]:
                widget.setValue(0.0)
            self.cmbEQueueType.setValue(eQueueTypeId)


    def getWorkPlan(self):
        dayPlans = [ self.getDayPlan(self.edtTimeRange1, self.edtQuantity1, self.chkOvertime1, self.dsbLimitSuperviseUnit1, self.edtPersonQuota1)
                    ]
        if self.rbDual.isChecked() or self.rbWeek.isChecked():
            dayPlans.append( self.getDayPlan(self.edtTimeRange2, self.edtQuantity2, self.chkOvertime2, self.dsbLimitSuperviseUnit2, self.edtPersonQuota2) )
        if self.rbWeek.isChecked():
            dayPlans.append( self.getDayPlan(self.edtTimeRange3, self.edtQuantity3, self.chkOvertime3, self.dsbLimitSuperviseUnit3, self.edtPersonQuota3) )
            dayPlans.append( self.getDayPlan(self.edtTimeRange4, self.edtQuantity4, self.chkOvertime4, self.dsbLimitSuperviseUnit4, self.edtPersonQuota4) )
            dayPlans.append( self.getDayPlan(self.edtTimeRange5, self.edtQuantity5, self.chkOvertime5, self.dsbLimitSuperviseUnit5, self.edtPersonQuota5) )
            dayPlans.append( self.getDayPlan(self.edtTimeRange6, self.edtQuantity6, self.chkOvertime6, self.dsbLimitSuperviseUnit6, self.edtPersonQuota6) )
            dayPlans.append( self.getDayPlan(self.edtTimeRange7, self.edtQuantity7, self.chkOvertime7, self.dsbLimitSuperviseUnit7, self.edtPersonQuota7) )
        return dayPlans, self.chkFillRedDays.isChecked()


    @staticmethod
    def getDayPlan(edtTimeRange, edtQuantity, chkOvertime, dsbLimitSuperviseUnit, edtPersonQuota):
        return ( edtTimeRange.timeRange(),
                 edtQuantity.value(),
                 chkOvertime.isChecked(),
                 dsbLimitSuperviseUnit.value(),
                 edtPersonQuota.value()
               )


    def getDateRange(self):
        return self.edtBegDate.date(), self.edtEndDate.date()


    def eQueueTypeId(self):
        return self.cmbEQueueType.value()


    # @QtCore.pyqtSlot(int)
    # def on_cmbEQueueType_currentIndexChanged(self, index):
        # eQueueTypeId = self.eQueueTypeId()
        # db = QtGui.qApp.db
        # tableJob = db.table('Job')
        # tableJobType = db.table('rbJobType')
        # cond = [tableJob['eQueueType_id'].eq(eQueueTypeId),
        #         tableJob['date'].dateBetween(*self.getDateRange()),
        #         tableJobType['id'].ne(self._currentJobTypeId)]
        # cols = [tableJobType['name'].alias('jobTypeName')]
        # recordList = db.getRecordList(table = tableJob.innerJoin(tableJobType, tableJobType['id'].eq(tableJob['jobType_id'])),
        #                               cols = cols,
        #                               where = cond,
        #                               group = tableJobType['id'])
        # if recordList:
        #     count = len(recordList)
        #     QtGui.QMessageBox.warning(self,
        #                               u'Уже используется',
        #                               u'Данный тип очереди уже используется другим%s тип%s работ:\n%s' % (u'' if count == 1 else u'и',
        #                                                                                                   u'ом' if count == 1 else u'ами',
        #                                                                                                   u'\n'.join([forceString(record.value('jobTypeName')) for record in recordList])),
        #                               QtGui.QMessageBox.Ok)
        #     self.cmbEQueueType.setCurrentIndex(0)


