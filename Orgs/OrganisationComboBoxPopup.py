# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtCore, QtGui

from KLADR.KLADRModel           import getKladrTreeModel, getInsuranceAreaTreeModel
from library.Utils              import forceStringEx, addDotsEx
from Registry.PolicySerialEdit  import CPolicySerialEdit



class COrganisationComboBoxPopupPolicySerialEdit(CPolicySerialEdit):
    def __init__(self, parent=None):
        CPolicySerialEdit.__init__(self, parent)


class COrganisationComboBoxListView(QtGui.QListView):
    __pyqtSignals__ = ('hide()',)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL('hide()'))
            evt.accept()
            return
        super(COrganisationComboBoxListView, self).keyPressEvent(evt)

from Ui_OrganisationComboBoxPopup import Ui_OrganisationComboBoxPopup


class COrganisationComboBoxPopup(QtGui.QFrame, Ui_OrganisationComboBoxPopup):
    __pyqtSignals__ = ('itemComboBoxSelected(int)',
                      )

    def __init__(self, parent=None, organisationFilter='', useInsuranceAreaModel=False):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setupUi(self)
        self.organisationFilter = organisationFilter
        self.model = parent.model()
        self._parent = parent
        self.tblOrganisation.setModel(self.model)
        self.tblOrganisation.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.connect(self.tblOrganisation, QtCore.SIGNAL('hide()'), self.hide)
        self._areaFilter = ''
        self._areaList   = None
        self.regAddress  = None
        self._serialFilter = ''
        self._serial = ''
        self.cond = []
        self.table = QtGui.qApp.db.table('Organisation')

        db = QtGui.qApp.db
        if useInsuranceAreaModel and db.getCount('kladr.KLADR', where='isInsuranceArea = 1'):
            model = getInsuranceAreaTreeModel()
        else:
            model = getKladrTreeModel()
        model.setAllSelectable(True)
        self.cmbArea._model = model
        self.cmbArea.setModel(model)
        self.cmbArea._popupView.treeModel = model
        self.cmbArea._popupView.treeView.setModel(model)

        self.setRegAdress()
        self.cmbArea.installEventFilter(self)
        self.edtInfis.installEventFilter(self)
        self.edtName.installEventFilter(self)
        self.edtINN.installEventFilter(self)
        self.edtOGRN.installEventFilter(self)
        self.edtOKATO.installEventFilter(self)
        self.edtPolisSerial.installEventFilter(self)
        self.isFirst = True



    def setOrganisationFilter(self, filter):
        self.organisationFilter = filter


    def show(self):
        self.tblOrganisation.setFocus()
        row = self._parent.currentIndex()
        if row >= 0:
            index = self.model.createIndex(row, 0)
        else:
            index = self.model.createIndex(0, 0)
        self.tblOrganisation.setCurrentIndex(index)
        QtGui.QFrame.show(self)


    def selectItemByIndex(self, index):
        id = self.model.getId(index.row())
        id = id if id else 0
        self.emit(QtCore.SIGNAL('itemComboBoxSelected(int)'), id)
        self.hide()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblOrganisation_clicked(self, index):
        self.selectItemByIndex(index)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()


    def on_buttonBox_reset(self):
        self.isFirst = False
        self._serialFilter = ''
        self._serial = ''
        self.chkArea.setChecked(False)
        self.cond = [self.organisationFilter]
        if self.regAddress:
            areaList = [QtGui.qApp.defaultKLADR()]
            regAddress = self.regAddress['KLADRCode']
            areaList.append(regAddress)
            self.setAreaFilter(areaList)
            self.cmbArea.setCode(regAddress)
        else:
#            self.setAreaFilter([QtGui.qApp.defaultKLADR(),
#                                self.cmbArea.code()])
            self.cmbArea.setCode(QtGui.qApp.defaultKLADR())
            self._areaFilter = ''
        self.updateFilter()
        self.edtInfis.clear()
        self.edtName.clear()
        self.edtINN.clear()
        self.edtOGRN.clear()
        self.edtOKATO.clear()
        self.edtPolisSerial.clear()


    def on_buttonBox_apply(self):
        self.isFirst = False
        table = self.table
        db = QtGui.qApp.db
        cond = []
        infisCode = unicode(forceStringEx(self.edtInfis.text()))
        name      = unicode(forceStringEx(self.edtName.text()))
        inn       = unicode(forceStringEx(self.edtINN.text()))
        ogrn    = unicode(forceStringEx(self.edtOGRN.text()))
        okato   = unicode(forceStringEx(self.edtOKATO.text()))
        serial    = unicode(forceStringEx(self.edtPolisSerial.text()))
        cond.append(self.organisationFilter)
        if infisCode:
            cond.append(table['infisCode'].like(infisCode))
        if inn:
            cond.append(table['INN'].eq(inn))
        if ogrn:
            cond.append(table['OGRN'].eq(ogrn))
        if okato:
            cond.append(table['OKATO'].eq(okato))
        if name:
            nameFilter = []
            dotedName = addDotsEx(name)
            nameFilter.append(table['shortName'].like(dotedName))
            nameFilter.append(table['fullName'].like(dotedName))
            nameFilter.append(table['title'].like(dotedName))
            cond.append(db.joinOr(nameFilter))
        if serial:
            serial = unicode(serial).upper()
            if self._serial != serial:
                self._serialFilter = self.constructSerialFilter(serial)
                self._serial = serial
        else:
            self._serialFilter = ''
            self._serial = ''
        self.cond = cond
        if self.chkArea.isChecked():
            areaList = [self.cmbArea.code()]
            self.setAreaFilter(areaList)
        else:
            self._areaFilter = ''
            self.updateFilter()
        self.model.update()


    def setRegAdress(self, regAddress=None):
        self.regAddress = regAddress
        if regAddress:
            self.cmbArea.setCode(regAddress['KLADRCode'])
        else:
            self.cmbArea.setCode(QtGui.qApp.defaultKLADR())


    def constructAreaFilter(self, areaList):
        if areaList:
            db = QtGui.qApp.db
            table = self.table
            return db.joinAnd([self.organisationFilter, table['area'].inlist(areaList+[''])])
        return None


    def setAreaFilter(self, areaList):
        l = set()
        for code in areaList:
            if code:
                l.add(code[:2].ljust(13, '0'))
                l.add(code[:5].ljust(13, '0'))
        areaList = list(l)
#        if self._areaList != areaList:
        self._areaFilter = self.constructAreaFilter(areaList)
        self._areaList = areaList
        self.updateFilter()


    def setSerialFilter(self, serial):
        self.isFirst = False
        serial = unicode(serial).upper()
        if self._serial != serial:
            innerSerial = forceStringEx(self.edtPolisSerial.text())
            if unicode(innerSerial).upper() != serial:
                self.edtPolisSerial.setText(serial)
            self._serialFilter = self.constructSerialFilter(serial)
            self._serial = serial
            self.updateFilter()


    def constructSerialFilter(self, serial):
        db = QtGui.qApp.db
        if serial:
            table = db.table('Organisation_PolicySerial')
            idlist1 = db.getIdList(table, 'organisation_id', table['serial'].eq(serial))
            table = db.table('Organisation')
#            idlist2 = db.getIdList(table, 'id', db.joinAnd([self.insurerFilter, 'NOT EXISTS (SELECT id FROM Organisation_PolicySerial WHERE Organisation_PolicySerial.organisation_id=Organisation.id)']))
            if idlist1:# or idlist2:
                return table['id'].inlist(idlist1)#+idlist2)
        return None


    def updateFilter(self):
        db = QtGui.qApp.db
        cond = self.cond
        if self._serialFilter:
            cond.append(self._serialFilter)
        if self._areaFilter:
            cond.append(self._areaFilter)
        currValue = self._parent.value()
        self.model.setFilter(db.joinAnd(cond))
        self.cond = [self.organisationFilter or '1=1']
        if self.model.rowCount() > 1:
            self.tabWidget.setCurrentIndex(0)
        self._parent.setValue(currValue)
        # x = 0 if self.isFirst else 1
        # if not self.parent.value() and self.model.rowCount()>x:
            # self.parent.setCurrentIndex(x)
            # self.tblOrganisation.setCurrentIndex(self.model.createIndex(x, 0))


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key in (QtCore.Qt.Key_C, QtCore.Qt.Key_G):
                # if key == QtCore.Qt.Key_C:
                #     obj.keyPressEvent(event)
                self.keyPressEvent(event)
                return False
            if  key == QtCore.Qt.Key_Tab:
                self.focusNextPrevChild(True)
                return True
        return False


    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self.tabWidget.currentIndex():
                self.on_buttonBox_apply()
            else:
                index = self.tblOrganisation.selectedIndexes()
                if index:
                    self.selectItemByIndex(index[0])
        if (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_C):
            self.tabWidget.setCurrentIndex(0)
        if (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_G):
            self.tabWidget.setCurrentIndex(1)
        QtGui.QFrame.keyPressEvent(self, event)

    def setOGRN(self, OGRN):
        self.edtOGRN.setText(OGRN)

    def setOKATO(self, OKATO):
        self.edtOKATO.setText(OKATO)

    def disableArea(self):
        self.chkArea.setChecked(False)
