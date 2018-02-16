# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Pharmacy import Ui_AddWhileTakingDialog

from library.DialogBase                    import CConstructHelperMixin
from library.TableModel                    import *


class CTimeTableModel(QtCore.QAbstractTableModel):

    items = []
    unit = ''
    horizontalHeaderText = [u'Доза']
    verticalHeaderText = ['00:00',
                          '01:00',
                          '02:00',
                          '03:00',
                          '04:00',
                          '05:00',
                          '06:00',
                          '07:00',
                          '08:00',
                          '09:00',
                          '10:00',
                          '11:00',
                          '12:00',
                          '13:00',
                          '14:00',
                          '15:00',
                          '16:00',
                          '17:00',
                          '18:00',
                          '19:00',
                          '20:00',
                          '21:00',
                          '22:00',
                          '23:00']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        for time in self.verticalHeaderText:
            self.items.append([time, ''])


    def setUnit(self, unit):
        self.unit = unit


    def columnCount(self, index = None):
        return len(self.horizontalHeaderText)


    def rowCount(self, index = None):
        return len(self.verticalHeaderText)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.horizontalHeaderText[section])
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.verticalHeaderText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row][1]
            return QtCore.QVariant(item)
        elif role == QtCore.Qt.EditRole:
            item = self.items[row][1]
            return QtCore.QVariant(item[0:item.find('(') - 1])
        return QtCore.QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if  forceString(value) != '' and (forceString(forceDouble(value)) == forceString(value) or forceString(forceInt(value)) == forceString(value)):
                row = index.row()
                self.items[row][1] = forceString(value) + ' (' + self.unit + ')'
                self.reset()
                return True
            else:
                row = index.row()
                self.items[row][1] = ''
                self.reset()
                return True


    def loadData(self, items):
        self.items = items
        self.reset()


    def getData(self):
        return self.items


    def getTimeList(self):
        timeList = []
        for time in self.verticalHeaderText:
            timeList.append([time, ''])
        return timeList


class CAddWhileTakingSetupDialog(QtGui.QDialog, Ui_AddWhileTakingDialog, CConstructHelperMixin):
    unit = ''

    def __init__(self, drugFormularyItemId, items = '', parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        stmt = u'''
                SELECT rbUnit.code
                FROM rbMedicines
                INNER JOIN DrugFormulary_Item ON rbMedicines.id = DrugFormulary_Item.drug_id
                INNER JOIN rbUnit ON rbUnit.id = rbMedicines.unit_id
                WHERE DrugFormulary_Item.id = %(id)s
                ''' % {'id' : drugFormularyItemId}
        query = QtGui.qApp.db.query(stmt)
        if query.first():
            record = query.record()
            self.unit = forceString(record.value('code'))
        else:
            self.unit = ''


        self.addModels('TimeTable', CTimeTableModel(self))
        self.tblTimeList.setModel(self.modelTimeTable)
        self.tblTimeList.model().setUnit(self.unit)
        if items != '':
            items = items.split(';')
            itemsOut = self.tblTimeList.model().getTimeList()
            for item in items:
                if item != items[-1]:
                    i = itemsOut.index([item[0:item.find('-') - 1].strip(), ''])
                    itemsOut[i][1] = item[item.find('-') + 1:-1].strip() + ')'
            self.tblTimeList.model().loadData(itemsOut)
        self.tblTimeList.horizontalHeader().setStretchLastSection(True)
        self.tblTimeList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

    def getData(self):
        items = self.tblTimeList.model().getData()
        data = ''
        for item in items:
            if item[1] != '':
                data += item[0] + ' - ' + item[1] + '; '
        return data

    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.accept()
        else:
            self.reject()