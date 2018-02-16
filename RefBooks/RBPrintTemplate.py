# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os
import codecs

from PyQt4 import QtGui, QtCore

from library.interchange        import getComboBoxValue, getLineEditValue, getRBComboBoxValue, getTextEditValue, \
                                       setComboBoxValue, setLineEditValue, setRBComboBoxValue, setTextEditValue, \
    setCheckBoxValue, getCheckBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.PrintTemplates     import CPrintTemplatesDataCache
from library.TableModel         import CEnumCol, CTextCol
from library.Utils              import forceString, forceStringEx, toVariant

from Ui_RBPrintTemplateEditor   import Ui_PrintTemplateEditorDialog


class CRBPrintTemplate(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(   u'Контекст',     ['context'], 20),
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'],   40),
            CTextCol(   u'Группа',       ['groupName'], 20),
            CTextCol(   u'Файл',         ['fileName'], 20),
            CEnumCol(   u'Меняет ДПД',   ['dpdAgreement'], [u'Не меняет',
                                                            u'Меняет на "Да"',
                                                            u'Меняет на "нет"'], 15),
            CEnumCol(   u'Тип',          ['type'],         [u'HTML',
                                                            u'Exaro',
                                                            u'SVG'], 15)
            ], 'rbPrintTemplate', ['context', 'code', 'name', 'groupName', 'type', 'id', 'isPatientAgreed'])
        self.setWindowTitleEx(u'Шаблоны печати')

        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.connect(self.actDuplicate, QtCore.SIGNAL('triggered()'), self.duplicateCurrentRow)

        self.actDelete = QtGui.QAction(u"Удалить", self)
        self.actDuplicate.setObjectName("actDelete")
        self.connect(self.actDelete, QtCore.SIGNAL("triggered()"), self.deleteCurrentRow)

        self.tblItems.createPopupMenu([self.actDuplicate, self.actDelete])


    def getItemEditor(self):
        return CPrintTemplateEditor(self)

    @QtCore.pyqtSlot()
    def deleteCurrentRow(self):

        if QtGui.QMessageBox.warning(None, u'Внимание!', u'Удалить шаблон?',
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:

            def deleteCurrentInternal():
                currentItemId = self.currentItemId()
                if currentItemId:
                    db = QtGui.qApp.db
                    table = db.table("rbPrintTemplate")
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('deleted', toVariant(1))
                    db.updateRecord(table, record)
                    self.renewListAndSetTo()
            QtGui.qApp.call(self, deleteCurrentInternal)


    def duplicateCurrentRow(self):
        def duplicateCurrentInternal():
            currentItemId = self.currentItemId()
            if currentItemId :
                db = QtGui.qApp.db
                table = db.table('rbPrintTemplate')
                db.transaction()
                try:
                    record = db.getRecord(table, '*', currentItemId)
                    record.setValue('code', toVariant(forceString(record.value('code'))+'_1'))
                    record.setValue('name', toVariant(forceString(record.value('name'))+'_1'))
                    record.setNull('id')
                    newItemId = db.insertRecord(table, record)
                    db.commit()
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
                self.renewListAndSetTo(newItemId)
        QtGui.qApp.call(self, duplicateCurrentInternal)

#
# ##########################################################################
#


class CPrintTemplateEditor(Ui_PrintTemplateEditorDialog, CItemEditorDialog):

    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, 'rbPrintTemplate')
#        self.setupUi(self)
        self.setWindowTitleEx(u'Шаблон печати')
#        self.setupDirtyCather()
        self.exaroEditor = forceString(QtGui.qApp.preferences.appPrefs.get('exaroEditor', ''))
        if not self.exaroEditor:
            self.btnEdit.setToolTip(u'Необходимо указать редактор отчетов Exaro на вкладке "Прочие настойки" в Умолчаниях')
            self.btnEdit.setEnabled(False)
        self.cmbCounter.setTable('rbCounter')
        self.cmbIEMKDoc.setTable('rbIEMKDocument')
        self.cmbCounter.setEnabled(False)       # По умолчанию нам не требуется сохранять обращение перед печатью, соответственно счетчик указывать нельзя.


    def setRecord(self, record):
        CItemEditorDialog.setRecord(self, record)
        setLineEditValue( self.edtContext,   record, 'context')
        setLineEditValue( self.edtFileName,  record, 'fileName')
        setTextEditValue( self.edtDefault,   record, 'default')
        setComboBoxValue( self.cmbDPD,       record, 'dpdAgreement')
        setComboBoxValue( self.cmbType,      record, 'type')
        setComboBoxValue(self.cmbBanUnkeptData, record, 'banUnkeptDate')
        setRBComboBoxValue(self.cmbCounter,  record, 'counter_id')
        setRBComboBoxValue(self.cmbIEMKDoc, record, 'documentType_id')
        setCheckBoxValue(self.chkPatientApply, record, 'isPatientAgreed')
        setLineEditValue(self.edtGroup, record, 'groupName')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorDialog.getRecord(self)
#        getLineEditValue( self.edtCode,      record, 'code')
#        getLineEditValue( self.edtName,      record, 'name')
        getLineEditValue( self.edtContext,   record, 'context')
        getLineEditValue( self.edtFileName,  record, 'fileName')
        getTextEditValue( self.edtDefault,   record, 'default')
        getComboBoxValue( self.cmbDPD,       record, 'dpdAgreement')
        getComboBoxValue( self.cmbType,      record, 'type')
        getComboBoxValue(self.cmbBanUnkeptData, record, 'banUnkeptDate')
        getRBComboBoxValue(self.cmbCounter,  record, 'counter_id')
        getRBComboBoxValue(self.cmbIEMKDoc, record, 'documentType_id')
        getCheckBoxValue(self.chkPatientApply, record, 'isPatientAgreed')
        getLineEditValue(self.edtGroup, record, 'groupName')
        CPrintTemplatesDataCache.reset()
        return record


    def checkDataEntered(self):
        result = CItemEditorDialog.checkDataEntered(self)
        result = result and (forceStringEx(self.edtContext.text()) or self.checkInputMessage(u'контекст', False, self.edtContext))
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbBanUnkeptData_currentIndexChanged(self, index):
        self.cmbCounter.setEnabled(index > 0)
        if index == 0:
            self.cmbCounter.setValue(None)


    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        fileName = forceString(self.edtFileName.text())
        try:
            if not fileName:
                tmpDir = QtGui.qApp.getTmpDir('edit')
                fullPath = os.path.join(tmpDir, 'template.bdrt')
                txt = self.edtDefault.toPlainText()
                file = codecs.open(unicode(fullPath), encoding='utf-8', mode='w+')
                file.write(unicode(txt))
                file.close()
                usingTempFile = True
            else:
                fullPath = os.path.join(QtGui.qApp.getTemplateDir(), fileName)

            cmdLine = u'"%s" "%s"' % (self.exaroEditor, fullPath)
            started, error, exitCode = QtGui.qApp.execProgram(cmdLine)
            if started:
                if not fileName:
                    for enc in ['utf-8', 'cp1251']:
                        try:
                            file = codecs.open(fullPath, encoding=enc, mode='r')
                            txt = file.read()
                            file.close()
                            self.edtDefault.setPlainText(txt)
                            return
                        except:
                            pass
                    QtGui.QMessageBox.critical(None,
                                           u'Внимание!',
                                           u'Не удалось загрузить "%s" после' % fullPath,
                                           QtGui.QMessageBox.Close)
            else:
                QtGui.QMessageBox.critical(None,
                                       u'Внимание!',
                                       u'Не удалось запустить "%s"' % self.exaroEditor,
                                       QtGui.QMessageBox.Close)
        finally:
            if not fileName:
                QtGui.qApp.removeTmpDir(tmpDir)

