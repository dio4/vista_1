# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
import re
from library.LineEdit import CLineEdit
from library.Utils import generalConnectionName

__author__ = 'atronah'

'''
    author: atronah
    date:   20.10.2014
'''



from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtSql



class CEQueueTypeOrgStructureWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        super(CEQueueTypeOrgStructureWidget, self).__init__(parent)

        self.setupUi(self)

        self._queueTypeModel = QtSql.QSqlTableModel(self, QtSql.QSqlDatabase.database(generalConnectionName(), open = True))
        self._queueTypeModel.setTable(u'rbEQueueType')
        self._queueTypeModel.select()

        self._baseOrgStructureId = None
        self._orgStructureModel = QtSql.QSqlTableModel(self, QtSql.QSqlDatabase.database(generalConnectionName(), open = True))
        self._orgStructureModel.setTable(u'OrgStructure')
        self._orgStructureModel.select()

        self.cmbQueue.setModel(self._queueTypeModel)
        self.cmbQueue.setModelColumn(self._queueTypeModel.fieldIndex('name'))
        self.on_cmbQueue_currentChanged(self.cmbQueue.currentIndex())

        self.cmbOrgStructure.setModel(self._orgStructureModel)
        self.cmbOrgStructure.setModelColumn(self._orgStructureModel.fieldIndex('name'))



    @staticmethod
    def setupUi(widget):
        layout = QtGui.QGridLayout()
        layout.setMargin(0)


        widget.lblQueue = QtGui.QLabel(u'&Очередь:', widget)
        widget.lblQueue.setObjectName("lblQueue")
        layout.addWidget(widget.lblQueue, 0, 0)

        widget.cmbQueue = QtGui.QComboBox(widget)
        widget.cmbQueue.setObjectName("cmbQueue")
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget.cmbQueue.sizePolicy().hasHeightForWidth())
        widget.cmbQueue.setSizePolicy(sizePolicy)
        layout.addWidget(widget.cmbQueue, 0, 1)
        widget.lblQueue.setBuddy(widget.cmbQueue)

        widget.lblOrgStructure = QtGui.QLabel(u'&Кабинет:', widget)
        widget.lblOrgStructure.setObjectName("lblOrgStructure")
        layout.addWidget(widget.lblOrgStructure, 1, 0)

        widget.cmbOrgStructure = QtGui.QComboBox(widget)
        widget.cmbOrgStructure.setObjectName("cmbOrgStructure")
        widget.cmbOrgStructure.setSizePolicy(sizePolicy)
        layout.addWidget(widget.cmbOrgStructure, 1, 1)
        widget.lblOrgStructure.setBuddy(widget.cmbOrgStructure)

        widget.setLayout(layout)

        QtCore.QMetaObject.connectSlotsByName(widget)


    def queueTypeId(self):
        row = self.cmbQueue.currentIndex()
        return self._queueTypeModel.record(row).value('id').toInt()[0]


    def setQueueTypeId(self, queueTypeId):
        if queueTypeId:
            idFieldIndex = self._queueTypeModel.fieldIndex('id')
            indexList = self._queueTypeModel.match(self._queueTypeModel.index(0, idFieldIndex),
                                                      QtCore.Qt.EditRole,
                                                      QtCore.QVariant(queueTypeId))
            if indexList:
                self.cmbQueue.setCurrentIndex(indexList[0].row())



    def setOrgStructureId(self, baseId = None, currentId = None):
        if baseId:
            self._baseOrgStructureId = baseId
            self._orgStructureModel.setFilter("id IN (SELECT OS_A.id "
                                              "       FROM OrgStructure_Ancestors AS OS_A"
                                              "       WHERE OS_A.fullPath RLIKE '[[:<:]]%s[[:>:]]'"
                                              "       )"
                                              "OR id = %s" % (baseId, baseId))
            self._orgStructureModel.select()
            if not currentId:
                currentId = self.orgStructureId()

        if not currentId:
            currentId = self._baseOrgStructureId
        if currentId:
            idFieldIndex = self._orgStructureModel.fieldIndex('id')
            indexList = self._orgStructureModel.match(self._orgStructureModel.index(0, idFieldIndex),
                                                      QtCore.Qt.EditRole,
                                                      QtCore.QVariant(currentId))
            if indexList:
                self.cmbOrgStructure.setCurrentIndex(indexList[0].row())



    def orgStructureId(self):
        row = self.cmbOrgStructure.currentIndex()
        return self._orgStructureModel.record(row).value('id').toInt()[0]


    def on_cmbQueue_currentChanged(self, index):
        baseOrgStructureId = self._queueTypeModel.record(index).value('orgStructure_id').toInt()[0]
        self.setOrgStructureId(baseId = baseOrgStructureId, currentId = None)




        

class CEQControlEditor(QtGui.QDialog):
    def __init__(self, parent = None, flags = QtCore.Qt.Window):
        super(CEQControlEditor, self).__init__(parent, flags)
        self.setupUi(self)


    @staticmethod
    def setupUi(widget):
        widget.setObjectName("EQControlEditor")
        widget.setWindowTitle(u'Параметры кнопки')
        widget.gridLayout = QtGui.QGridLayout(widget)
        widget.gridLayout.setObjectName("gridLayout")

        widget.eQueueTypeOrgStructure = CEQueueTypeOrgStructureWidget()
        widget.setObjectName("eQueueTypeOrgStructure")
        widget.gridLayout.addWidget(widget.eQueueTypeOrgStructure, 0, 0, 1, 3)

        widget.edtName = CLineEdit(widget)
        widget.edtName.setObjectName("edtName")
        widget.edtName.setPlaceholderText(u'Имя')
        widget.gridLayout.addWidget(widget.edtName, 1, 0, 1, 3)

        widget.edtHost = CLineEdit(widget)
        widget.edtHost.setObjectName("edtHost")
        widget.edtHost.setPlaceholderText(u'Хост')
        widget.gridLayout.addWidget(widget.edtHost, 2, 0, 1, 1)

        widget.lblColon = QtGui.QLabel(u':', widget)
        widget.lblColon.setObjectName("lblColon")
        widget.gridLayout.addWidget(widget.lblColon, 2, 1, 1, 1)

        widget.edtPort = CLineEdit(widget)
        widget.edtPort.setObjectName("edtPort")
        widget.edtPort.setPlaceholderText(u'Порт')
        widget.edtPort.setInputMask(u'0000D')
        widget.gridLayout.addWidget(widget.edtPort, 2, 2, 1, 1)

        widget.buttonBox = QtGui.QDialogButtonBox(widget)
        widget.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        widget.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        widget.buttonBox.setObjectName("buttonBox")
        widget.gridLayout.addWidget(widget.buttonBox, 3, 0, 1, 3)

        widget.buttonBox.accepted.connect(widget.accept)
        widget.buttonBox.rejected.connect(widget.reject)
        QtCore.QMetaObject.connectSlotsByName(widget)


    def disableRemoteSettings(self):
        self.edtHost.setEnabled(False)
        self.edtPort.setEnabled(False)
        self.lblColon.setEnabled(False)


    def name(self):
        return self.edtName.text()


    def setName(self, name):
        self.edtName.setText(name)


    def host(self):
        return self.edtHost.text()


    def setHost(self, host):
        self.edtHost.setText(host)


    def orgStructureId(self):
        return self.eQueueTypeOrgStructure.orgStructureId()


    def setOrgStructureId(self, baseId = None, currentId = None):
        self.eQueueTypeOrgStructure.setOrgStructureId(baseId, currentId)


    def queueTypeId(self):
        return self.eQueueTypeOrgStructure.queueTypeId()


    def setQueueTypeId(self, queueTypeId):
        self.eQueueTypeOrgStructure.setQueueTypeId(queueTypeId)


    def port(self):
        return self.edtPort.text().toInt()[0]


    def setPort(self, port):
        self.edtPort.setText(u'%s' % port)



    def accept(self):
        errorMessages = []
        if self.edtPort.isEnabled():
            port, isOk = self.edtPort.text().toInt()
            if not (isOk and port):
                errorMessages.append(u'Некорректно указан порт (д.б. числовым и больше нуля).')
        if self.edtHost.isEnabled():
            host = self.edtHost.text()
            hostMatch = re.match(ur'((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)',
                                 host)
            if not (hostMatch and hostMatch.end() == len(host)):
                errorMessages.append(u'Некорректно указан IP-адрес кнопки.')

        if not self.orgStructureId():
            errorMessages.append(u'Некорректно указано подразделение {%s}' % self.orgStructureId())

        if errorMessages:
            QtGui.QMessageBox.warning(self, u'Некорректные данные', u'\n'.join(errorMessages))
        else:
            super(CEQControlEditor, self).accept()










def main():
    import sys

    sys.exit(0)


if __name__ == '__main__':
    main()