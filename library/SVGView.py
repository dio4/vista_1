# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Softwa     All rights reserved.
##
#############################################################################

import codecs
import os.path
import re

from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtSvg
from PyQt4 import QtXml

from Ui_SVGView import Ui_SVGViewDialog


def showSVG(widget, name, content, pageFormat):
    view = CSVGView(pageFormat, widget)
    view.setDocName(name)
    view.setContent(content)
    view.exec_()
        
def printSVG(name, content, printer):
    doc = CSVGDocument(content)
    doc.print_(name, printer)


class CSVGDocument(QtXml.QDomDocument):
    def __init__(self, content=None):
            QtXml.QDomDocument.__init__(self)
            if content:
                self.setContent(content)


    def setContent(self, content):
        self.srcContent = content
        ok, errorMsg, errorLine, errorColumn = QtXml.QDomDocument.setContent(self, QByteArray(content.encode('utf-8')), False)
        if not ok:
            raise Exception(u'%s at (%d, %d)' % (errorMsg, errorLine, errorColumn))


    def isValid(self):
        svgElement = self.firstChildElement('svg')
        return svgElement is not None and not svgElement.isNull()


    def findPages(self):
        pageIdList = []
        svgElement = self.firstChildElement('svg')
        if svgElement:
            pageElement = svgElement.firstChildElement('g')
            while pageElement and not pageElement.isNull():
                pageId = unicode(pageElement.attribute('id'))
                if pageId.startswith('page'):
                    pageIdList.append(pageId)
#                    pageElement.setAttribute('visibility', 'hidden')
                pageElement = pageElement.nextSiblingElement('g')
        return pageIdList


    def getPageRectSizeF(self):
        def parseLength(txt):
            s = re.search(r'^\s*((?:\d+\.?\d*)|(?:\d*\.\d+))\s*([^ ]*)\s*$',txt)
            if s:
                qnt, unit = s.groups()
                result = float(qnt) if qnt and qnt != '.' else 0
                if unit == 'mm':
                    return result
                elif unit == 'sm':
                    return result*10
                elif unit == 'in':
                    return result*25.4
                else:
                    return result*25.4/72
            else:
                return None

        width = height = None
        svgElement = self.firstChildElement('svg')
        if svgElement:
            width = parseLength(unicode(svgElement.attribute('width')))
            height = parseLength(unicode(svgElement.attribute('height')))
        if width and height:
            return QSizeF(width, height)
        else:
            return None


    def hideAllPagesExceptOne(self, visiblePageId):
        svgElement = self.firstChildElement('svg')
        if svgElement:
            pageElement = svgElement.firstChildElement('g')
            while pageElement and not pageElement.isNull():
                pageId = unicode(pageElement.attribute('id'))
                if pageId.startswith('page'):
                    if pageId == visiblePageId:
                        pageElement.setAttribute('visibility', 'visible')
                    else:
                        pageElement.setAttribute('visibility', 'hidden')
                pageElement = pageElement.nextSiblingElement('g')


    def print_(self, docName, printer):
        size = self.getPageRectSizeF()
        if size:
            printer.setPaperSize(size,0)

#        if size:
#            if printer.outputFileName():
#                printer.setPaperSize(size,0)
#            else:
#                w = size.width()
#                h = size.height()
#                if w < h:
#                    size.transpose()
#                    printer.setOrientation(QtGui.QPrinter.Landscape)
#                else:
#                    printer.setOrientation(QtGui.QPrinter.Portrait)
#                printer.setPaperSize(size,0)
#        else:
#            printer.setPaperSize(QtGui.QPrinter.A4)
#            printer.setOrientation(QtGui.QPrinter.Portrait)

        printer.setFullPage(True)
        printer.setPageMargins(0,0,0,0,0)
        printer.setCreator('vista-med')
        printer.setDocName(docName)
        printer.setFontEmbeddingEnabled(True)
        painter = QtGui.QPainter()

        renderer = QtSvg.QSvgRenderer()
        painter.begin(printer)
#        if printer.orientation() == QtGui.QPrinter.Landscape:
#            painterRect = painter.viewport()
#            painter.translate(0, painterRect.height())
#            painter.rotate(270)

        pageIdList = self.findPages()
        if pageIdList:
            fromPage = printer.fromPage()
            toPage   = printer.fromPage()
            if fromPage and toPage:
                pageIdList = pageIdList[fromPage-1:toPage]
            if printer.pageOrder == QtGui.QPrinter.LastPageFirst:
                pageIdList.reverse()
            firstPage = True
            for pageId in pageIdList:
                self.hideAllPagesExceptOne(pageId)
                renderer.load(self.toByteArray(0))
                if not firstPage:
                    printer.newPage()
                renderer.render(painter)
                firstPage = False
        else:
            renderer.load(self.toByteArray())
            renderer.render(painter)
#        del renderer
        painter.end()


class CSVGView(QtGui.QDialog, Ui_SVGViewDialog):
    def __init__(self, pageFormat, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.btnPrint = QtGui.QPushButton(u'Печатать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.btnPrint.setDefault(True)

#        self.btnEMail = QtGui.QPushButton(u'Отправить', self)
#        self.btnEMail.setObjectName('btnEMail')
#        self.btnEMail.setEnabled(False)

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.graphicsView.setScene(QtGui.QGraphicsScene(self.graphicsView))
        style = self.style()
        #self.btnFirstPage.setIcon(style.standardIcon(QtGui.QStyle.SP_MediaSkipBackward))
        #self.btnLastPage.setIcon(style.standardIcon(QtGui.QStyle.SP_MediaSkipForward))
        self.doc = CSVGDocument()
        self.pageFormat = pageFormat
        self.pageIdList = []
        self.initItems()
        self.setupPagesControl()
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
#        self.buttonBox.addButton(self.btnEMail, QtGui.QDialogButtonBox.ActionRole)
#        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.setDocName('SVG View')


    def initItems(self):
        darkGray = QtGui.QColor(64,64,64)
        boundingRect = QRectF(0,0,10,10)
        self.graphicsView.setBackgroundBrush(QtGui.QBrush(Qt.darkGray))
        scene = self.graphicsView.scene()
        scene.clearSelection() #scene.clear()!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        self.svgItem = QtSvg.QGraphicsSvgItem()
        self.svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
#        self.svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svgItem.setZValue(0)

        self.shadowItem = QtGui.QGraphicsRectItem(boundingRect.adjusted(-1, -1, 2, 2))
        self.shadowItem.setBrush(QtGui.QBrush(darkGray))
        self.shadowItem.setPen(QtGui.QPen(darkGray))
        self.shadowItem.setZValue(-2)
        self.shadowItem.setPos(4, 4)

        self.frameItem = QtGui.QGraphicsRectItem(boundingRect.adjusted(-1, -1, 2, 2))
        self.frameItem.setBrush(QtGui.QBrush(Qt.white))
        self.frameItem.setPen(QtGui.QPen(darkGray))
        self.frameItem.setZValue(-1)
        self.frameItem.setPos(-1, -1)

        scene.addItem(self.shadowItem)
        scene.addItem(self.frameItem)
        scene.addItem(self.svgItem)
        scene.setSceneRect(boundingRect.adjusted(-3, -3, 10, 10))


    def setDocName(self, name):
        self.docName = name
        self.setWindowTitle(name)
        fileName = name
        for x in ':?|()[]\"\';!*/\\':
            fileName = fileName.replace(x, '')
        self.fileName = fileName


    def setContent(self, content):
        try:
            self.doc.setContent(content)
        except:
            pass

        if self.doc.isValid():
            self.pageIdList = self.doc.findPages()
            self.svgItem.renderer().load(QByteArray(content.encode('utf-8')))
            self.svgItem.setElementId('') # for recalc item.boundRect()
            boundingRect = self.svgItem.boundingRect()
            self.shadowItem.setRect(boundingRect.adjusted(-1, -1, 2, 2))
            self.frameItem.setRect(boundingRect.adjusted(-1, -1, 2, 2))
            self.graphicsView.scene().setSceneRect(boundingRect.adjusted(-3, -3, 10, 10))
            self.setupPagesControl()


    def setupPagesControl(self):
        self.gotoPage(0)
        self.edtPageNum.setRange(1, len(self.pageIdList))
        self.grpPager.setVisible(len(self.pageIdList)>1)
        self.grpPager.setEnabled(len(self.pageIdList)>1)


    def gotoPage(self, n):
        self.btnFirstPage.setEnabled(n>0)
#        self.btnPrevPage.setEnabled(n>0)
#        self.btnNextPage.setEnabled(n+1<len(self.pageIdList))
        self.btnLastPage.setEnabled(n+1<len(self.pageIdList))
        self.edtPageNum.setValue(n+1)
        if 0<=n<len(self.pageIdList):
            self.doc.hideAllPagesExceptOne(self.pageIdList[n])
            self.svgItem.renderer().load(self.doc.toByteArray(0))
            self.svgItem.setElementId('')


    def saveAsFile(self):
        defaultFileName = QtGui.qApp.getSaveDir()
        if self.fileName:
            defaultFileName = os.path.join(defaultFileName, self.fileName)

        saveFormats = [u'изображение SVG (*.svg)',
                       u'Portable Document Format (*.pdf)',
                       u'PostScript (*.ps)',
                      ]
        selectedFilter = QString('')

        fileName = QtGui.QFileDialog.getSaveFileName(
            self,
            u'Выберите имя файла',
            defaultFileName,
            ';;'.join(saveFormats),
            selectedFilter)
        if not fileName.isEmpty():
            exts = selectedFilter.section('(*.',1,1).section(')',0,0).split(';*.')
            ext = QFileInfo(fileName).suffix()
            if exts and not exts.contains(ext, Qt.CaseInsensitive):
                ext = exts[0]
                fileName.append('.'+ext)
            fileName = unicode(fileName)
            ext = unicode(ext)
            if ext.lower() == 'pdf':
                self.saveAsPdfOrPS(fileName, QtGui.QPrinter.PdfFormat)
            elif ext.lower() == 'ps':
                self.saveAsPdfOrPS(fileName, QtGui.QPrinter.PostScriptFormat)
            else:
                self.saveAsSvg(fileName)


    def saveAsPdfOrPS(self, fileName, format):
        QtGui.qApp.setSaveDir(fileName)
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setOutputFormat(format)
        printer.setOutputFileName(fileName)
        printer.setFontEmbeddingEnabled(True)
        self.pageFormat.setupPrinter(printer)
        self.doc.print_(self.docName, printer)


    def saveAsSvg(self, fileName):
        QtGui.qApp.setSaveDir(fileName)
        file = codecs.open(unicode(fileName), encoding='utf-8', mode='w+')
        file.write(self.doc.srcContent)
        file.close()


    @pyqtSlot()
    def on_btnFirstPage_clicked(self):
        self.edtPageNum.setValue(self.edtPageNum.minimum())


#    @pyqtSlot()
#    def on_btnPrevPage_clicked(self):
#        self.edtPageNum.setValue(self.edtPageNum.value()-1)


#    @pyqtSlot()
#    def on_btnNextPage_clicked(self):
#        self.edtPageNum.setValue(self.edtPageNum.value()+1)


    @pyqtSlot()
    def on_btnLastPage_clicked(self):
        self.edtPageNum.setValue(self.edtPageNum.maximum())


    @pyqtSlot(int)
    def on_edtPageNum_valueChanged(self, val):
        self.gotoPage(val-1)


    @pyqtSlot()
    def on_btnPrint_clicked(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        self.pageFormat.setupPrinter(printer)
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setMinMax(1, max(1, len(self.pageIdList)))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        self.doc.print_(self.docName, printer)


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.reject()
        elif buttonCode == QtGui.QDialogButtonBox.Retry:
            self.accept()
        elif buttonCode == QtGui.QDialogButtonBox.Save:
            QtGui.qApp.call(self, self.saveAsFile)
        else:
            pass

