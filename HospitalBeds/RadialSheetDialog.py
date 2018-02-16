# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.DialogBase         import CDialogBase
from library.TableModel         import CTableModel, CDateCol, CTextCol

from Ui_RadialSheetDialog       import Ui_dialogRadialSheet
from Ui_RadialSheetSetupDialog  import Ui_dialogSetupRadialSheet


class CRadialSheetSetupDialog(QtGui.QDialog,  Ui_dialogSetupRadialSheet):
    def __init__(self,  parent,  personName):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.personName = personName
        self.tableProperties = {}

    @QtCore.pyqtSlot()
    def on_btnOK_clicked(self):
        self.tableProperties['Spots']  = {}
        self.tableProperties['fields'] = {}
        for i in xrange(self.spinPoints.value()):
            self.tableProperties['Spots'][i] = ''
        for i in xrange(self.spinFields.value()):
            self.tableProperties['fields'][i] = ''
        dialog = CRadialSheetDialog(self, self.personName,  self.tableProperties )
        dialog.exec_()
        self.reject()

class CRadialSheetDialog(CDialogBase,  Ui_dialogRadialSheet):
    def __init__(self,  parent,  personName, tableProperties ):
        CDialogBase.__init__(self, parent)
        #Ui_dialogRadialSheet.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        #self.addModels('RadialSheet',  CRadialSheetTableModel({'MU': {'1': 1,  '2': 2,},  'Spots':{'1':1,  '2':2}},  self))
        #self.addModels('RadiationSource',  CRadiationSourceTableModel('',  self))

        
#        self.setModels(self.tblRadialSheet,  self.modelRadialSheet,  self.selectionModelRadialSheet)
#        self.setModels(self.tblRadiationSource,  self.modelRadiationSource,  self.selectionModelRadiationSource)
        self.testDataContents = {}
        self.testDataContents['fields'] = {}
        self.testDataContents['Spots'] = {}
        for i in range(30):
            self.testDataContents['fields'][i] = ''
            self.testDataContents['Spots'][i] = ''
        
        self.modelRadialSheet = CRadialSheetTableModel(self.testDataContents,  self)
        self.tblRadialSheet.setModel(self.modelRadialSheet)
        self.tblRadialSheet.resizeColumnsToContents()
        self.modelRadiationSource = CRadiationSourceTableModel('',  self)
        self.tblRadiationSource.setModel(self.modelRadiationSource)
        self.lblPerson.setText(personName)      


class CRadiationSourceTableModel(QtCore.QAbstractTableModel):
    def __init__(self,  data,  parent=None):
        QtCore.QAbstractTableModel.__init__(self,  parent)
        self.rows = [u'Источник излучения',  
                            u'Область излучения', 
                            u'',
                            u'', 
                            u'расположение поля', 
                            u'размеры поля', 
                            u'направление пучка', 
                            u'Характер движения источника', 
                            u'РИП(РИо)']

    def rowCount(self,  tmp):
        return len(self.rows)
        
    def columnCount(self,  tmp):
        return 1
        
    def data(self, index, role):
        #d = self.arraydata[index.row()][index.column()]
        #return QVariant(self.arraydata[index.row()][index.column()])
        if (role == QtCore.Qt.DisplayRole):
            return ""
        return QtCore.QVariant()
        
    def headerData(self,  section,  orientation,  role=QtCore.Qt.DisplayRole):
        if (orientation==QtCore.Qt.Vertical and role==QtCore.Qt.DisplayRole):
            return self.rows[section]
            
            
class CRadialSheetTableModel(CTableModel):
    def __init__(self, datain, parent=None): 
        self.arraydata = datain
        
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'№ п/п', ['code'],  20))
        self.addColumn(CDateCol(u'Дата', ['date'], 20))
        self.fieldCount = len(datain['fields'].keys())
        self.pointCount = len(datain['Spots'].keys())
        for i in datain['fields'].keys():
            self.addColumn(CTextCol(u'Мониторные единицы',  ['mu_val'],  25))
        for i in datain['Spots'].keys():
            self.addColumn(CTextCol(u'Разовая доза',  ['singlePortion'],  10))
            self.addColumn(CTextCol(u'Суммарная доза',  ['totalPortion'],  10))
        self.addColumn(CTextCol(u'Подпись',  ['sign'],  10)),
    
    def flags(self, index):
        row = index.row()
        #record = self.getRecordByRow(row)
        enabled = True
        if enabled:
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsSelectable
    
        #self.setTable('rbPatientModel')
        
    def rowCount(self,  tmp):
        return 30
    def columnCount(self,  tmp):
        return len(self.arraydata['fields'].keys()) + len(self.arraydata['Spots'].keys()*2) + 3
        
    def data(self, index, role):
        #d = self.arraydata[index.row()][index.column()]
        #return QVariant(self.arraydata[index.row()][index.column()])
        if (role == QtCore.Qt.DisplayRole):
            if (index.column()==0):
                return QtCore.QVariant(index.row()+1)
            elif (index.column() ==1):
                return QtCore.QDate.currentDate().addDays(index.row()).toString('dd.MM.yyyy')
            elif (index.column()>1 and index.column<(2+self.fieldCount)):
                return self.arraydata['fields'][index.row()]
            elif (index.column()>=(2+self.fieldCount) and index.column()<(2+self.fieldCount+self.pointCount*2)) :
                return self.arraydata['Spots'][index.row()]
            else:
                return ''
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignHCenter + QtCore.Qt.AlignVCenter)
        return QtCore.QVariant()
        
