# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2015 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4              import QtGui, QtCore

from library.constants import dateRightInfinity, dateLeftInfinity
from library.dbfpy.dbf  import Dbf
from library.Utils      import forceString

from Utils import getDBFFileFromZipArchive, getFilesZipArchive

from Ui_ImportMKB import Ui_ImportMKB

def importMKB(widget):
    dialog = CImportMKB(widget)
    dialog.exec_()

class CImportMKB(QtGui.QDialog, Ui_ImportMKB):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.btnImport.setEnabled(False)
        self.importDBF = None

    def openFile(self, fileName):

        archive, nameFiles = getFilesZipArchive(fileName)
        if archive:
            for name in nameFiles:
                if not unicode(name.lower()).endswith('spr20.dbf'):
                    continue
                self.importDBF = getDBFFileFromZipArchive(archive, name)
                break
        else:
            if unicode(fileName.lower()).endswith('spr20.dbf'):
                self.importDBF = Dbf(fileName, encoding='cp866')
        if not self.importDBF:
            self.logBrowser.append(u'В архиве нет spr20.dbf файла.' if archive else u'Необходимо выбрать файл spr20.dbf.')
            self.logBrowser.update()
            return
        self.btnImport.setEnabled(True)

    def updateMKB(self, mapMKB):
        db = QtGui.qApp.db
        self.progressBar.setRange(0, len(mapMKB))
        self.logBrowser.append(u'Конструирование запроса')
        dateLeft = dateLeftInfinity.toString('yyyy-MM-dd')
        dateRight = dateRightInfinity.toString('yyyy-MM-dd')
        stmt = u'UPDATE MKB_Tree SET begDate=\'%s\', endDate=\'%s\', OMS=\'1\' WHERE parent_code IS NULL;\n' % (dateLeft, dateRight)
        for i, code in enumerate(mapMKB):
            stmt += u'UPDATE MKB SET OMS=\'{OMS}\', begDate=\'{begDate}\', endDate=\'{endDate}\', DiagName=\'{name}\' WHERE DiagID=\'{code}\';\n' \
                    u'UPDATE MKB_Tree SET OMS=\'{OMS}\', begDate=\'{begDate}\', endDate=\'{endDate}\', DiagName=\'{name}\' WHERE DiagID=\'{code}\';\n'.format(
                        OMS=mapMKB[code][0],
                        begDate=mapMKB[code][1] or dateLeft,
                        endDate=mapMKB[code][2] or dateRight,
                        code=code,
                        name=mapMKB[code][3]
                    )
            self.progressBar.setValue(i)
            if not i % 30:
                db.query(stmt)
                stmt = ''
        db.query(stmt)

    def insertMKB(self, mapMKB):
        self.progressBar.setRange(0, 0)
        mapMKB = mapMKB.copy()
        db = QtGui.qApp.db
        self.logBrowser.append(u'Конструирование запроса')
        tbl_tree = db.table('MKB_Tree')
        view_tree = db.table('vMKBTree')
        tbl = view_tree.leftJoin(tbl_tree, view_tree['BlockID'].eq(tbl_tree['DiagID']))
        blocks = dict(
            (forceString(rec.value(1)), forceString(rec.value(0)).strip('()').split('-'))
            for rec in db.getRecordList(tbl, 'DISTINCT vMKBTree.BlockID, MKB_Tree.id'))
        exist = (forceString(rec.value(0)) for rec in db.getRecordList(tbl_tree, 'DiagID'))
        for diag in exist:
            if diag in mapMKB:
                del mapMKB[diag]

        def get_block(code):
            for tree_id, mkb_range in blocks.iteritems():
                if (len(mkb_range) == 1 and mkb_range[0] == code) or (len(mkb_range) == 2 and mkb_range[0] <= code <= mkb_range[1]):
                    return tree_id
            return None

        values = []

        dateLeft = dateLeftInfinity.toString('yyyy-MM-dd')
        dateRight = dateRightInfinity.toString('yyyy-MM-dd')

        self.progressBar.setRange(0, len(mapMKB))
        for k, v in mapMKB.iteritems():
            if len(k) == 3:
                parent = get_block(k)
                if not parent:
                    continue
            elif len(k) == 5:
                parent = k[:3]
            elif len(k) == 6:
                parent = k[:5]
            else:
                continue
            values.append('(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)' % (
                k,                  # DiagID
                v[3],               # DiagName
                parent,
                v[0],               # OMS
                v[1] or dateLeft,   # begDate
                v[2] or dateRight   # endDate
            ))
            self.progressBar.step()
        if values:
            stmt = u'INSERT INTO MKB_Tree (DiagID, DiagName, parent_code, OMS, begDate, endDate, Prim, sex, age, characters, duration, USL_OK1, USL_OK2, USL_OK3, USL_OK4, SELF) ' \
                   u'VALUES ' + ', '.join(values)
            db.query(stmt)



    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        db = QtGui.qApp.db
        mapMKB = {}
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(self.importDBF))
        self.progressBar.setValue(0)
        self.logBrowser.append(u'Импорт начат: %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss')))
        self.logBrowser.update()
        insertValues = []
        self.progressBar.setText(u'Считывание данных из файла')
        for recordDBF in self.importDBF:
            self.progressBar.step()
            try:
                code = forceString(recordDBF['CODE'])
                mapMKB[code] = (forceString(recordDBF['IS_OMS']),
                                forceString(recordDBF['DATN']),
                                forceString(recordDBF['DATO']),
                                forceString(recordDBF['NAME']))
            except KeyError:
                self.logBrowser.append(u'Неправильный формат файла\nИмпорт прерван: %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss')))
                self.logBrowser.update()
                self.importDBF.close()
                return
        self.importDBF.close()
        db.transaction()
        try:
            self.progressBar.setText(u'Обновление записей')
            self.updateMKB(mapMKB)
            self.progressBar.setText(u'Вставка записей')
            self.insertMKB(mapMKB)
            self.logBrowser.append(u'Импорт окончен: %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss')))
            self.logBrowser.update()
            db.commit()
        except:
            self.logBrowser.append(u'Ошибка импорта: %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss')))
            db.rollback()
            QtGui.qApp.logCurrentException()
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF, ZIP (*.dbf *.zip)')
        if fileName:
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.openFile(unicode(fileName))

