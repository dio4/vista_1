#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.DialogBase import CDialogBase
from library.Utils import *

from Ui_ImageProcDialog import Ui_ImageProcDialog


class CImageProcDialog(CDialogBase, Ui_ImageProcDialog):
    imageDir = ''

    def __init__(self, parent, image):
        CDialogBase.__init__(self, parent)
        self.btnLoad =  QtGui.QPushButton(u'Загрузить', self)
        self.btnLoad.setObjectName('btnLoad')
        self.btnSave =  QtGui.QPushButton(u'Сохранить', self)
        self.btnSave.setObjectName('btnSave')
        self.btnClear = QtGui.QPushButton(u'Очистить',  self)
        self.btnClear.setObjectName('btnClear')
        self.scene =    QtGui.QGraphicsScene(self)
        self.scene.setObjectName('scene')

        self.setupUi(self)
#        self.setWindowFlags(Qt.Popup)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitleEx(u'Просмотр изображения')
        self.buttonBox.addButton(self.btnLoad,  QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnSave,  QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnClear, QtGui.QDialogButtonBox.ActionRole)
        self.grpView.setScene(self.scene)
        self._pixmapItem = None
        self._image = None
        self.setImage(image)


    def setImage(self, image):
        scene = self.grpView.scene()
        if self._pixmapItem:
            scene.removeItem(self._pixmapItem)
            self._pixmapItem = None
        if image:
            pixmap = QtGui.QPixmap.fromImage(image)
            self._pixmapItem = scene.addPixmap(pixmap)
        self._image = image
        self.btnSave.setEnabled(bool(self._image))


    def image(self):
        return self._image


    @QtCore.pyqtSlot(int)
    def on_scrSize_valueChanged(self, value):
        s = 2.0**(value*0.25)
        self.grpView.resetMatrix()
        self.grpView.scale(s, s)


    @QtCore.pyqtSlot()
    def on_btnLoad_clicked(self):
        if not CImageProcDialog.imageDir:
            CImageProcDialog.imageDir = QtGui.qApp.getSaveDir()
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(
                                self,
                                u'Укажите файл с изображением',
                                CImageProcDialog.imageDir,
                                u'Файлы изображений (*.bmp *.jpg *.jpeg *.png *.ppm *.tiff *.xpm);;Все файлы (* *.*)'))
        if fileName != '' :
            CImageProcDialog.imageDir = fileName
            image = QtGui.QImage()
            if image.load(fileName):
                self.setImage(image)
            else:
                pass

    @QtCore.pyqtSlot()
    def on_btnSave_clicked(self):
        if self._image:
            saveFormats = [u'Windows Bitmap (*.bmp)',
                           u'Joint Photographic Experts Group (*.jpg, *.jpeg)',
                           u'Portable Network Graphics (*.png)',
                           u'Portable Pixmap (*.ppm)',
                           u'Tagged Image File Format (*.tiff)',
                           u'X11 Pixmap (*.xpm)',
                          ]
            selectedFilter = QString('')

            if not CImageProcDialog.imageDir:
                CImageProcDialog.imageDir = QtGui.qApp.getSaveDir()

            fileName = QtGui.QFileDialog.getSaveFileName(
                self,
                u'Выберите имя файла',
                CImageProcDialog.imageDir,
                ';;'.join(saveFormats),
                selectedFilter)
            if not fileName.isEmpty():
                exts = selectedFilter.section('(*.',1,1).section(')',0,0).split(';*.')
                ext = QFileInfo(fileName).suffix()
                if exts and not exts.contains(ext, Qt.CaseInsensitive):
                    ext = exts[0]
                    fileName.append('.'+ext)
                fileName = unicode(fileName)
                self._image.save(fileName)


    @QtCore.pyqtSlot()
    def on_btnClear_clicked(self):
        self.setImage(None)

