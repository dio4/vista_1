# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.DialogBase import CDialogBase
from library.TreeModel  import CDBTreeModel, CDBTreeItem
from library.Utils      import forceRef, forceString

from Ui_ComplaintsEditDialog import Ui_ComplaintsEditDialog


class CComplaintsEditDialog(CDialogBase, Ui_ComplaintsEditDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.addModels('Complains', CComplaintsModel(self))
        self.setupUi(self)
        self.setModels(self.treeTypicalComplaints, self.modelComplains,  self.selectionModelComplains)
        self.treeTypicalComplaints.expandAll()


    def disableCancel(self):
        button = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        if button:
            button.setEnabled(False)


    def setComplaints(self,text):
        self.edtComplaints.setPlainText(text)


    def getComplaints(self):
        return unicode(self.edtComplaints.toPlainText())

    def getCito(self):
        return (self.chkCito.isChecked())

    def setCito(self, isUrgent):
        self.chkCito.setChecked(isUrgent)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeTypicalComplaints_doubleClicked(self, index):
        parts = []
        item = index.internalPointer()
        while item and item.id():
            parts.append(unicode(item.name()))
            item = item.parent()
        parts.reverse()
        text = ': '.join(parts)
        cursor = self.edtComplaints.textCursor()

        if cursor.hasSelection():
            pos = cursor.selectionStart()
            cursor.removeSelectedText()
            cursor.setPosition(pos)
        elif not cursor.atBlockStart():
            cursor.movePosition(QtGui.QTextCursor.EndOfWord)
            cursor.insertText(', ')
        cursor.insertText(text)



class CComplaintsModel(CDBTreeModel):
    def __init__(self, parent):
        CDBTreeModel.__init__(self, parent, 'rbComplain', 'id', 'group_id', 'name', 'code')
        self.setRootItemVisible(False)


    def loadChildrenItems(self, group):
        result = []
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        alias = table.alias(self.tableName+'2')
        children = table.alias(self.tableName + '_children')
        cond = [table[self.groupColName].eq(group.id())]
        for record in db.getRecordList(table,
                                       [self.idColName, self.nameColName,
                                        '(' + db.selectStmt(children,
                                                            db.count('*'),
                                                            table[self.idColName].eq(children[self.groupColName])
                                                            ) + ')'],
                                       cond,
                                       self.order):
            item = self.getItemFromRecord(record, group)
            result.append(item)
        return result


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if section == 0 and orientation == QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            return QtCore.QVariant(u'Типичные жалобы')
        else:
            return QtCore.QVariant()
