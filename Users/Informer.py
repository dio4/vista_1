# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QVariant

from library.database           import CTableRecordCache
from library.DialogBase         import CDialogBase
from library.interchange        import getLineEditValue, getTextEditHTML, setLineEditValue, setTextEditHTML
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog, CItemsListDialogEx
from library.TableModel         import CDateTimeCol, CRefBookCol, CTextCol
from library.Utils              import forceRef, forceString, toVariant

from Ui_InformerEditor          import Ui_InformerMessageEditorDialog
from Ui_InformerViewer          import Ui_InformerPage
from Ui_InformerEditorInsertLink import Ui_InsertLinkDialog


class CInformerList(CItemsListDialogEx):
    def __init__(self, parent, forSelect=False):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol( u'Автор',        ['createPerson_id'], 'vrbPerson', 10),
            CDateTimeCol(u'Дата и время', ['createDatetime'], 20),
            CTextCol(    u'Тема',         ['subject'], 20),
            ], 'InformerMessage', ['createDatetime DESC'])
        self.setWindowTitleEx(u'Список сообщений информатора')
        self.tblItems.addPopupDelRow()
        self.addPopupAction('actViewMessageRead', u'Список прочитавших', self.view_message_read)

    def view_message_read(self):
        CInformerMessageReadDialog(self, self.currentItemId()).exec_()

    def getItemEditor(self):
        return CInformerEditor(self)


class CInformerMessageReadDialog(CItemsListDialog):
    def __init__(self, parent, message_id):
        self.message_id = message_id

        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(u'Имя', ['person_id'], 'vrbPerson', 10),
        ], 'InformerMessage_readMark', ['person_id ASC'], True)
        self.setWindowTitleEx(u'Список прочитавших сообщение информатора')
        self.btnEdit.setVisible(False)
        self.btnNew.setVisible(False)
        self.btnPrint.setVisible(False)
        self.btnSelect.setVisible(False)

    def select(self, props):
        table = self.model.table()
        where = 'master_id = %d' % self.message_id
        return QtGui.qApp.db.getIdList(table.name(), self.idFieldName, where, self.order)

    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_doubleClicked(self, index):
        pass


#
# ##########################################################################
#

class CInsertLinkDialog(QtGui.QDialog, Ui_InsertLinkDialog):
    def __init__(self, parent, text):
        super(CInsertLinkDialog, self).__init__(parent)
        self.setupUi(self)
        self.edtText.setText(text)


class CInformerEditor(CItemEditorBaseDialog, Ui_InformerMessageEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'InformerMessage')
        self.setupUi(self)

        self.user_profiles = []
        db = QtGui.qApp.db
        q = db.query(db.selectStmt('rbUserProfile', 'id, name'))
        while q.next():
            self.user_profiles.append(q.value(0).toInt()[0])
            self.cbxUserGroup.addItem(q.value(1).toString())

        self.edtText.currentCharFormatChanged.connect(self.current_char_format_changed)
        self.edtText.cursorPositionChanged.connect(self.cursor_position_changed)
        self.setWindowTitleEx(u'Сообщение информатора')
        self.setupDirtyCather()

        self.block_font_size = False


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue( self.edtSubject, record, 'subject')
        setTextEditHTML(  self.edtText,    record, 'text')

        addressee = record.value('addressee').toInt()[0]
        self.cbxUserGroup.setCurrentIndex(
            self.user_profiles.index(addressee) + 1 if addressee else 0
        )

        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue( self.edtSubject, record, 'subject')
        getTextEditHTML(  self.edtText,    record, 'text')

        idx = self.cbxUserGroup.currentIndex()
        record.setValue('addressee', QVariant(self.user_profiles[idx-1] if idx > 0 else None))

        return record


    def checkDataEntered(self):
        return True

    def cursor_position_changed(self):
        if self.edtText.alignment() & QtCore.Qt.AlignLeft:
            self.btnAlignLeft.setChecked(True)
        elif self.edtText.alignment() & QtCore.Qt.AlignHCenter:
            self.btnAlignCenter.setChecked(True)
        elif self.edtText.alignment() & QtCore.Qt.AlignRight:
            self.btnAlignRight.setChecked(True)
        elif self.edtText.alignment() & QtCore.Qt.AlignJustify:
            self.btnAlignJustify.setChecked(True)

    def current_char_format_changed(self, fmt):
        font = fmt.font()

        self.block_font_size = True
        self.spinFontSize.setValue(font.pointSize())
        self.btnBold.setChecked(font.bold())
        self.btnItalic.setChecked(font.italic())
        self.btnUnderstroke.setChecked(font.underline())

    def apply_format(self, fmt):
        cursor = self.edtText.textCursor()
        if not cursor.hasSelection():
            cursor.select(QtGui.QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(fmt)
        self.edtText.mergeCurrentCharFormat(fmt)

    @QtCore.pyqtSlot()
    def on_btnBold_clicked(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontWeight(QtGui.QFont.Bold if self.btnBold.isChecked() else QtGui.QFont.Normal)
        self.apply_format(fmt)

    @QtCore.pyqtSlot()
    def on_btnItalic_clicked(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontItalic(self.btnItalic.isChecked())
        self.apply_format(fmt)

    @QtCore.pyqtSlot()
    def on_btnUnderstroke_clicked(self):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontUnderline(self.btnUnderstroke.isChecked())
        self.apply_format(fmt)

    @QtCore.pyqtSlot()
    def on_btnAlignLeft_clicked(self):
        self.edtText.setAlignment(QtCore.Qt.AlignLeft)

    @QtCore.pyqtSlot()
    def on_btnAlignCenter_clicked(self):
        self.edtText.setAlignment(QtCore.Qt.AlignHCenter)

    @QtCore.pyqtSlot()
    def on_btnAlignRight_clicked(self):
        self.edtText.setAlignment(QtCore.Qt.AlignRight)

    @QtCore.pyqtSlot()
    def on_btnAlignJustify_clicked(self):
        self.edtText.setAlignment(QtCore.Qt.AlignJustify)

    @QtCore.pyqtSlot(int)
    def on_spinFontSize_valueChanged(self, size):
        if self.block_font_size:
            self.block_font_size = False
            return
        fmt = QtGui.QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self.apply_format(fmt)

    @QtCore.pyqtSlot(str)
    def on_cbxFont_activated(self, family):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontFamily(family)
        self.apply_format(fmt)

    @QtCore.pyqtSlot()
    def on_btnLink_clicked(self):
        c = self.edtText.textCursor()  # type: QtGui.QTextCursor
        dialog = CInsertLinkDialog(self, c.selectedText())
        if dialog.exec_() == QtGui.QDialog.Accepted:
            c.insertHtml('<a href="%s">%s</a> ' % (dialog.edtURL.text(), dialog.edtText.text()))

#
# ##########################################################################
#

def showInformer(widget, quiet):
    db = QtGui.qApp.db
    table = db.table('InformerMessage')
    tableReadMark = db.table('InformerMessage_readMark')
    messageIdList = db.getIdList( table.leftJoin(tableReadMark,
                                                 [tableReadMark['master_id'].eq(table['id']), tableReadMark['person_id'].eq(QtGui.qApp.userId)]),
                                  table['id'].name(),
                                  db.joinAnd((
                                      db.joinOr((
                                          table['addressee'].inlist(QtGui.qApp.userInfo._profiles),
                                          table['addressee'].isNull(),
                                      )),
                                      tableReadMark['id'].isNull(),
                                  )),
                                  table['createDatetime'].name()
                                )
    if messageIdList:
        informer = CInformer(widget)
        informer.setIdList(messageIdList)
        informer.exec_()
    elif not quiet:
        QtGui.QMessageBox.information(widget,
                    u'Информатор',
                    u'Нет непрочитанных сообщений',
                    QtGui.QMessageBox.Close)


class CInformer(CDialogBase, Ui_InformerPage):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.btnPrev = QtGui.QPushButton(u'Предыдущее', self)
        self.btnPrev.setObjectName('btnPrev')
        self.btnNext =  QtGui.QPushButton(u'Следующее',  self)
        self.btnNext.setObjectName('btnNext')
        self.setupUi(self)
        self.buttonBox.addButton(self.btnPrev, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnNext, QtGui.QDialogButtonBox.ActionRole)
        db = QtGui.qApp.db
        self.messageCache = CTableRecordCache(db, db.table('InformerMessage'))
        self.personCache = CTableRecordCache(db, db.table('vrbPerson'))
        self.idList = []
        self.markList = []
        self.currentIndex = None
        self.setWindowTitleEx(u'Сообщение')


    def setIdList(self, idList):
        self.idList = idList
        self.markList = [None]*len(self.idList)
        self.setCurrentIndex(0)


    def setCurrentIndex(self, index):
        notFirst = index>0
        notLast  = index<len(self.idList)-1
        self.currentIndex = index
        self.btnPrev.setEnabled(notFirst)
        self.btnNext.setEnabled(notLast)
        message = self.messageCache.get(self.idList[self.currentIndex])
        if message:
            createPersonId = forceRef(message.value('createPerson_id'))
            person = self.personCache.get(createPersonId)
            if person:
                personName = forceString(person.value('name'))
            else:
                personName = ''
            createDateTime = message.value('createDatetime').toDateTime()
            subject        = forceString(message.value('subject'))
            text           = forceString(message.value('text'))
        else:
            personName     = ''
            createDateTime = QtCore.QDateTime()
            subject        = ''
            text           = ''
        self.lblCreatePersonValue.setText(personName)
        self.lblCreateDatetimeValue.setText(createDateTime.toString(QtCore.Qt.LocaleDate))
        self.lblSubjectValue.setText(subject)
        self.edtText.setHtml(text)
        self.chkMarkViewed.setChecked(self.markList[self.currentIndex]!=False)
        if notLast:
            self.btnNext.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Close).setFocus(QtCore.Qt.OtherFocusReason)


    def canClose(self):
        for messageId, mark in zip(self.idList, self.markList):
            if mark == True: # т.к. бывает True/False/None
                self.markViewed(messageId)
            elif mark == False: # т.к. бывает True/False/None
                self.unmarkViewed(messageId)
        return True


    def markViewed(self, messageId):
        db = QtGui.qApp.db
        table = db.table('InformerMessage_readMark')
        if not db.getRecordEx(table, '*', [table['master_id'].eq(messageId), table['person_id'].eq(QtGui.qApp.userId)]):
            record = table.newRecord()
            record.setValue('master_id', toVariant(messageId))
            record.setValue('person_id', toVariant(QtGui.qApp.userId))
            db.insertRecord(table, record)


    def unmarkViewed(self, messageId):
        db = QtGui.qApp.db
        table = db.table('InformerMessage_readMark')
        db.deleteRecord(table, [table['master_id'].eq(messageId), table['person_id'].eq(QtGui.qApp.userId)])


    @QtCore.pyqtSlot(bool)
    def on_chkMarkViewed_toggled(self, checked):
        self.markList[self.currentIndex] = checked


    @QtCore.pyqtSlot()
    def on_btnPrev_clicked(self):
        if self.currentIndex>0:
            self.markList[self.currentIndex] = self.chkMarkViewed.isChecked()
            self.setCurrentIndex(self.currentIndex-1)


    @QtCore.pyqtSlot()
    def on_btnNext_clicked(self):
        if self.currentIndex<len(self.idList)-1:
            self.markList[self.currentIndex] = self.chkMarkViewed.isChecked()
            self.setCurrentIndex(self.currentIndex+1)


    @QtCore.pyqtSlot()
    def on_buttonBox_rejected(self):
        self.markList[self.currentIndex] = self.chkMarkViewed.isChecked()
        self.close()