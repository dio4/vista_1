# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import codecs
import os.path
import re
from PyQt4 import QtCore, QtGui

from Ui_ReportView import Ui_ReportViewDialog
from Users.Rights import urAdmin, urEditReportForm
from library.LoggingModule import Logger
from library.Utils import forceBool, getVal


class CPageFormat(object):
    # page size
    A3 = QtGui.QPrinter.A3
    A4 = QtGui.QPrinter.A4
    A5 = QtGui.QPrinter.A5
    A6 = QtGui.QPrinter.A6
    # page orientation
    Portrait = QtGui.QPrinter.Portrait
    Landscape = QtGui.QPrinter.Landscape
    #
    validPageSizes = { A3: A3, 'A3': A3,
                       A4: A4, 'A4': A4,
                       A5: A5, 'A5': A5,
#                       A6: A6, 'A6': A6
                     }
    validOrientations = { Portrait: Portrait,  'PORTRAIT': Portrait,  'P':Portrait,
                          Landscape:Landscape, 'LANDSCAPE':Landscape, 'L':Landscape
                     }

    def __init__(self, pageSize=QtGui.QPrinter.A4,
                        orientation=QtGui.QPrinter.Portrait,
                        leftMargin=10,
                        topMargin=10,
                        rightMargin=10,
                        bottomMargin=10
                ):
        self.pageSize = pageSize
        self.pageRect = None # для custom size
        self.orientation = orientation
        self.leftMargin = leftMargin
        self.topMargin = topMargin
        self.rightMargin = rightMargin
        self.bottomMargin = bottomMargin


    def setupPrinter(self, printer):
        printer.setPageSize(self.pageSize)
        if self.pageSize == QtGui.QPrinter.Custom and self.pageRect:
            printer.setPaperSize(self.pageRect, QtGui.QPrinter.Millimeter)
        printer.setOrientation(self.orientation)


    def updateFromPrinter(self, printer):
        self.pageSize = printer.pageSize()
        if self.pageSize == QtGui.QPrinter.Custom:
            self.pageRect = printer.paperSize(QtGui.QPrinter.Millimeter)
        else:
            self.pageRect = None
        self.orientation = printer.orientation()


    def setPageSize(self, size):
        if isinstance(size, basestring):
            size = size.upper().strip()
            customSize = re.match(r'^(\d+)\s*[xX]\s*(\d+)$', size)
            if customSize:
                self.pageSize = QtGui.QPrinter.Custom
                sizes = customSize.groups()
                self.pageRect = QtCore.QSizeF(float(sizes[0]), float(sizes[1]))
                return ''
        validPageSize = self.validPageSizes.get(size, None)
        if validPageSize is not None:
            self.pageSize = validPageSize
            self.pageRect = None
            return ''
        else:
            return u'[Invalid page size "%s"]' % size


    def setOrientation(self, orientation):
        if isinstance(orientation, basestring):
            orientation = orientation.upper().strip()
        validOrientation = self.validOrientations.get(orientation, None)
        if validOrientation != None:
            self.orientation = validOrientation
            return ''
        else:
            return u'[Invalid orientation "%s"]' % orientation


    def setMargins(self, margin):
        if isinstance(margin, (int, float)):
            self.leftMargin = margin
            self.topMargin = margin
            self.rightMargin = margin
            self.bottomMargin = margin
            return ''
        else:
            return u'[Invalid margin "%s"]' % margin


    def setLeftMargin(self, margin):
        if isinstance(margin, (int, float)):
            self.leftMargin = margin
            return ''
        else:
            return u'[Invalid left margin "%s"]' % margin


    def setTopMargin(self, margin):
        if isinstance(margin, (int, float)):
            self.topMargin = margin
            return ''
        else:
            return u'[Invalid top margin "%s"]' % margin


    def setRightMargin(self, margin):
        if isinstance(margin, (int, float)):
            self.rightMargin = margin
            return ''
        else:
            return u'[Invalid right margin "%s"]' % margin


    def setBottomMargin(self, margin):
        if isinstance(margin, (int, float)):
            self.bottomMargin = margin
            return ''
        else:
            return u'[Invalid bottom margin "%s"]' % margin


def odtAvailable():
    try:
        if 'QTextDocumentWriter' not in QtGui.__dict__:
            return False
        return 'ODF' in QtGui.QTextDocumentWriter.supportedDocumentFormats()
    except:
        pass
    return False


class CReportViewDialog(QtGui.QDialog, Ui_ReportViewDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.btnPrint = QtGui.QPushButton(u'Печатать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.btnPrint.setDefault(False)

        self.btnFastPrint = QtGui.QPushButton(u'Быстрая Печать', self)
        self.btnFastPrint.setObjectName('btnFastPrint')
        self.btnFastPrint.setDefault(True)

        self.btnEMail = QtGui.QPushButton(u'Отправить', self)
        self.btnEMail.setObjectName('btnEMail')
        self.btnEMail.setEnabled(False)

        self.btnEdit = QtGui.QPushButton(u'Редактировать', self)
        self.btnEdit.setObjectName('btnEdit')
        self.btnEdit.setEnabled((QtGui.qApp.userHasRight(urEditReportForm) or QtGui.qApp.userHasRight(urAdmin)) and bool(QtGui.qApp.documentEditor()))

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnFastPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnEMail, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnEdit, QtGui.QDialogButtonBox.ActionRole)
        if QtGui.qApp.userHasRight(urAdmin):
            # Если создавать btnShowQuery и не добавлять его в buttonbox, он все равно виден на форме в левом верхнем углу, да еще и перетягивает на себя фокус.
            self.btnShowQuery = QtGui.QPushButton(u'Показать запрос', self)
            self.btnShowQuery.setObjectName('btnShowQuery')
            self.btnShowQuery.setCheckable(True)
            self.buttonBox.addButton(self.btnShowQuery, QtGui.QDialogButtonBox.ActionRole)
            self.btnShowQuery.clicked.connect(self.on_btnShowQuery_clicked)
        
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.fileName = ''
        self.pageFormat = None
        self.orientation = QtGui.QPrinter.Portrait
        self.actionButtons = []
        self.actions = []
        
        self._document = None
        self._queryText = u'<Не удалось получить текст запроса>'

        self.repeatFunction = None
        self.txtReport.document().setDefaultFont(QtGui.qApp.defaultPrintFont())
        # self.re = re.compile('(>\d+\.\d<|>\d+\.\d\d<)') # 12.22 | 12.2

    def setWindowTitle(self, title):
        QtGui.QDialog.setWindowTitle(self, title)
        for x in ':?|()[]\"\';!*/\\':
            title = title.replace(x, '')
        self.fileName = title

    def setOrientation(self, orientation):
        self.orientation = orientation

    def setActions(self, actions):
        for action in actions:
            button = QtGui.QPushButton(action.getName(), self)
            button.setEnabled(action.isEnabled())
            self.buttonBox.addButton(button, QtGui.QDialogButtonBox.ActionRole)
            self.actionButtons.append(button)
            self.actions.append(action)

    def setRepeatButtonVisible(self, value=True, function=None):
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save|QtGui.QDialogButtonBox.Retry)
        self.repeatFunction = function

    def setText(self, reportResult):
        # reportResult.setHtml(self.changeDotToComma(reportResult.toHtml()))

        if isinstance(reportResult, (list, tuple)):
            text = reportResult[0]
            actions = reportResult[1:]
        else:
            text = reportResult
            actions = []

        if actions:
            self.setActions(actions)

        if isinstance(text, QtGui.QTextDocument):
            text.setDefaultFont(QtGui.qApp.defaultPrintFont())
            self.txtReport.setDocument(text.clone(self.txtReport))
            if self.fileName:
                Logger.logReport(report_name=self.fileName, login_id=Logger.loginId)
#            text.setParent(self.txtReport)
        else:
            self.txtReport.setHtml(text)
            
        self._document = None

    def setQueryText(self, queryText):
        if queryText:
            self._queryText = queryText

    def setCanvases(self, canvases):
        self.txtReport.setCanvases(canvases)

    def setPageFormat(self, format):
        self.pageFormat = format

    def saveAsFile(self):
        defaultFileName = QtGui.qApp.getSaveDir()
        if self.fileName:
            defaultFileName = os.path.join(unicode(defaultFileName), unicode(self.fileName))

        saveFormats = [u'Веб-страница (*.html;*.htm)',
                       u'Portable Document Format (*.pdf)',
                       u'PostScript (*.ps)',
                       u'Microsoft Excel (*.xls)',
                      ]
        if odtAvailable():
            saveFormats.insert(-1, u'Текстовый документ OpenOffice.org (*.odt)')
        selectedFilter = QtCore.QString('')

        fileName = QtGui.QFileDialog.getSaveFileName(
            self,
            u'Выберите имя файла',
            defaultFileName,
            ';;'.join(saveFormats),
            selectedFilter)
        if not fileName.isEmpty():
            exts = selectedFilter.section('(*.',1,1).section(')',0,0).split(';*.')
            ext = QtCore.QFileInfo(fileName).suffix()
            if exts and not exts.contains(ext, QtCore.Qt.CaseInsensitive):
                ext = exts[0]
                fileName.append('.'+ext)
            fileName = unicode(fileName)
            ext = unicode(ext)
            if ext.lower() == 'pdf':
                self.saveAsPdfOrPS(fileName, QtGui.QPrinter.PdfFormat)
            elif ext.lower() == 'ps':
                self.saveAsPdfOrPS(fileName, QtGui.QPrinter.PostScriptFormat)
            # elif ext.lower() == 'xls':
            #     self.saveAsXLS(fileName)
            elif ext.lower() == 'odt':
                self.saveAsOdt(fileName)
            else:
                if ext.lower() == 'xls':
                    from ExelReport import CExelReport
                    exelReport = CExelReport()
                    self.txtReport.setHtml(exelReport.saveAsExel(self.txtReport.toHtml()))
                self.saveAsHtml(fileName)

    # Метод исключительно для экселевских файлов.
    # Меняем точку на запятую
    # 12.0 -> 12,0
    # def changeDotToComma(self, html):
    #    numbers = self.re.findall(html)
    #    for x in numbers:
    #        temp = str(x).replace('.', ',')
    #        html = html.replace(x, temp)
    #    return html

    def saveAsHtml(self, fileName):
        QtGui.qApp.setSaveDir(fileName)
        baseDir, name = os.path.split(fileName)
        imageRelativePath = name.split('.', 1)[0]+'.files'
        imagesPath = os.path.join(baseDir, imageRelativePath)
        imagesDirCreated = False
        imageCounter = 0
        textDocument = self.txtReport.document()

        outTextDocument = textDocument.clone(textDocument)
        block = outTextDocument.begin()
        while block != outTextDocument.end():
            it = block.begin()
            while not it.atEnd():
                fragment = it.fragment()
                if fragment.isValid():
                    fm = fragment.charFormat().toImageFormat()
                    if fm.isValid() and not fm.name().isEmpty():
                        if not imagesDirCreated:
                            try:
                                os.mkdir(imagesPath)
                            except:
                                pass
                            imagesDirCreated = True
                        image = textDocument.resource(QtGui.QTextDocument.ImageResource, QtCore.QUrl(fm.name()))
                        imageFileName = imagesPath + '/'+str(imageCounter)+'.png'
                        writer = QtGui.QImageWriter(imageFileName, 'png')
                        writer.write(QtGui.QImage(image))
                        fm.setName('./'+imageRelativePath+'/'+str(imageCounter)+'.png')
                        cursor = QtGui.QTextCursor(outTextDocument)
                        cursor.setPosition(fragment.position())
                        cursor.setPosition(fragment.position() + fragment.length(), QtGui.QTextCursor.KeepAnchor)
                        cursor.setCharFormat(fm)
                        imageCounter+=1
                it+=1
            block = block.next()
        txt = outTextDocument.toHtml(QtCore.QByteArray('utf-8'))
        file = codecs.open(unicode(fileName), encoding='utf-8', mode='w+')
        file.write(unicode(txt))
        file.close()

    def saveAsOdt(self, fileName):
        writer = QtGui.QTextDocumentWriter();
        try:
            QtGui.qApp.setSaveDir(fileName)
            writer.setFormat('odf')
            writer.setFileName(fileName)
            writer.write(self.txtReport.document())
        finally:
            writer = None
            # sip.delete(writer)
            pass

    def setupPage(self, printer):
        printer.setOrientation(self.orientation)
        if self.pageFormat:
            self.pageFormat.setupPrinter(printer)

    def saveAsPdfOrPS(self, fileName, format):
        QtGui.qApp.setSaveDir(fileName)
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setOutputFormat(format)
        printer.setOutputFileName(fileName)
        self.setupPage(printer)
        self.printReport(printer)

    def printReport(self, printer):
        printTextDocument(self.txtReport.document(), self.fileName, self.pageFormat, printer)

    @QtCore.pyqtSlot()
    def on_btnFastPrint_clicked(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        self.setupPage(printer)
        self.printReport(printer)
        Logger.updateReport(self.fileName)

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        self.setupPage(printer)

        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'printPreview', False)):
            preview = QtGui.QPrintPreviewDialog(printer, self)
            self.connect(preview, QtCore.SIGNAL("paintRequested (QPrinter *)"), self.printReport)
            preview.exec_()
        else:
            dialog = QtGui.QPrintDialog(printer, self)
            if dialog.exec_() != QtGui.QDialog.Accepted:
                return
            self.printReport(printer)

        Logger.updateReport(self.fileName)

    @QtCore.pyqtSlot()
    def on_btnEMail_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        editor = QtGui.qApp.documentEditor()
        if editor is not None:
            tmpDir = QtGui.qApp.getTmpDir('reportEdit')
            tmpFileName = os.path.join(tmpDir, 'report.html')
            self.saveAsHtml(tmpFileName)
            cmdLine = u'"%s" "%s"'% (editor, tmpFileName)
            prg=QtGui.qApp.execProgram(cmdLine)
            if not prg[0]:
                QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Не удалось запустить "%s"' % editor,
                                       QtGui.QMessageBox.Close)
            if prg[2]:
                QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Ошибка при выполнении "%s"' % editor,
                                       QtGui.QMessageBox.Close)
            QtGui.qApp.removeTmpDir(tmpDir)
        else:
            QtGui.QMessageBox.critical(self,
                                    u'Ошибка!',
                                    u'Не указан исполнимый файл редактора документов\n'+
                                    u'Смотрите пункт меню "Настройки.Умолчания", закладка "Прочие настройки",\n'+
                                    u'строка "Внешний редактор документов".',
                                    QtGui.QMessageBox.Close)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.reject()
        elif buttonCode == QtGui.QDialogButtonBox.Retry:
            self.accept()
            if self.repeatFunction:
                self.repeatFunction()
        elif buttonCode == QtGui.QDialogButtonBox.Save:
            QtGui.qApp.call(self, self.saveAsFile)
        else:
            if button in self.actionButtons:
                i = self.actionButtons.index(button)
                self.actions[i].exec_(self)

    

    @QtCore.pyqtSlot()
    def on_btnShowQuery_clicked(self):
        checked = self.btnShowQuery.isChecked()
        if checked:
            self._document = self.txtReport.document().clone(self)
            self.txtReport.setPlainText(self._queryText)
        elif isinstance(self._document, QtGui.QTextDocument):
            self.setText(self._document)
        


def printTextDocument(document, documentName, pageFormat, printer):
    printer.setCreator(u'САМСОН-ВИСТА')
    printer.setDocName(documentName)
    outDocument = document
    document.setDefaultFont(QtGui.qApp.defaultPrintFont())
    if pageFormat:
        pageFormat.updateFromPrinter(printer)
        outDocument = document.clone(document)
        pd = document.documentLayout().paintDevice()
        if pd is None:
            pd = QtGui.qApp.desktop()
            document.documentLayout().setPaintDevice(pd)
        pd_logicalDpiX = pd.logicalDpiX()
        pd_logicalDpiY = pd.logicalDpiY()
        p_logicalDpiX = printer.logicalDpiX()
        p_logicalDpiY = printer.logicalDpiY()

        pageRect = printer.pageRect() # in pixels
        paperRect = printer.paperRect() # in pixels

        # hardware defined margins, in printer pixels
        hl = (pageRect.left()   - paperRect.left())
        ht = (pageRect.top()    - paperRect.top())
        hr = (paperRect.right() - pageRect.right())
        hb = (paperRect.bottom() -pageRect.bottom())

        # software defined margins, in printer pixels
        sl = pageFormat.leftMargin * p_logicalDpiX / 25.4 # 25.4 mm = 1 inch
        st = pageFormat.topMargin * p_logicalDpiY / 25.4
        sr = pageFormat.rightMargin * p_logicalDpiX / 25.4
        sb = pageFormat.bottomMargin * p_logicalDpiY / 25.4

        # margins
        ml = max(0, sl-hl)
        mt = max(0, st-ht)
        mr = max(0, sr-hr)
        mb = max(0, sb-hb)

        fmt = outDocument.rootFrame().frameFormat()
        fmt.setLeftMargin(ml / p_logicalDpiX * pd_logicalDpiX) #Sets the frame's left margin in in some parrots (screen pixels?)
        fmt.setTopMargin(mt/ p_logicalDpiY * pd_logicalDpiY)
        fmt.setRightMargin(mr / p_logicalDpiX * pd_logicalDpiX)
        fmt.setBottomMargin(mb / p_logicalDpiY * pd_logicalDpiY)
        outDocument.rootFrame().setFrameFormat(fmt)
        # Calculate page width and height, in screen pixels
        pw = float(pageRect.width()) / p_logicalDpiX * pd_logicalDpiX
        ph = float(pageRect.height()) / p_logicalDpiY * pd_logicalDpiY
        # setup page size
        outDocument.setPageSize(QtCore.QSizeF(pw, ph))
    outDocument.print_(printer)


class CReportViewOrientation(CReportViewDialog):
    def __init__(self, parent, orientation=QtGui.QPrinter.Portrait):
        CReportViewDialog.__init__(self, parent)
        self.orientation = orientation


    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setOrientation(self.orientation)
        printer.setPageMargins(10.0, 10.0, 10.0, 10.0, QtGui.QPrinter.Millimeter)
        self.setupPage(printer)
        dialog = QtGui.QPrintDialog(printer, self)
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        self.printReport(printer)

class CReportViewOrientationMargins(CReportViewOrientation):
    def __init__(self, parent, orientation=QtGui.QPrinter.Portrait, margins=None):
        # margins = list{left, top, right, bottom, unit}  unit - удиницы измерения
        CReportViewOrientation.__init__(self, parent, orientation)
        self.margins = margins


    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setOrientation(self.orientation)
        if self.margins:
            defaultMargins = printer.getPageMargins(QtGui.QPrinter.Millimeter)
            printer.setPageMargins(self.margins[0] if self.margins[0] != None else defaultMargins[0],
                                   self.margins[1] if self.margins[1] != None else defaultMargins[1],
                                   self.margins[2] if self.margins[2] != None else defaultMargins[2],
                                   self.margins[3] if self.margins[3] != None else defaultMargins[3],
                                   self.margins[4])
        else:
            printer.setPageMargins()
        self.setupPage(printer)
        dialog = QtGui.QPrintDialog(printer, self)
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        self.printReport(printer)