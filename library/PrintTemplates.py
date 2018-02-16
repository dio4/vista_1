# -*- coding: utf-8 -*-

import StringIO
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import sys
from base64 import b64encode, b64decode
from urllib import *

from library import PrintHelpers
from library.DbEntityCache import CDbEntityCache

try:
    exaroSupportError = u'QtScript: '
    # noinspection PyUnresolvedReferences
    import PyQt4.QtScript # для cx_freeze, exaro неявно зависит от QtScript
    exaroSupportError = u'Exaro: '
    # noinspection PyUnresolvedReferences
    import exaro
    exaroSupport = True
    exaroSupportError = u'-'
except ImportError,  e:
    exaroSupport = False
    exaroSupportError += str(e).decode('cp1251') if sys.platform == 'win32' else str(e)


from Reports.ReportView    import CPageFormat, CReportViewDialog, printTextDocument
from Orgs.Utils            import COrgInfo, COrgStructureInfo
from Orgs.PersonInfo       import CPersonInfo
from library.PrintInfo     import CInfoContext, CInfo, CDateInfo, CTimeInfo
from library.DialogsInfo   import CDialogsInfo
from library.TextDocument  import CTextDocument
from library.AmountToWords import amountToWords, currencyRUR
from library.SVGView       import showSVG, printSVG
from library.code128       import code128
from library.Utils         import *


u"""Шаблоны печати"""
u"template: tuple(name, id, dpdAgreement, banUnkeptDat) описание полей в rbPrintTemplate"

htmlTemplate = 0
exaroTemplate = 1
svgTemplate = 2

class CPrintTemplatesDataCache(CDbEntityCache):
    mapTableToData = {}

    @classmethod
    def getData(cls, context):
        context = tuple(context)
        result = cls.mapTableToData.get(context, None)
        if result is None:
            result = []
            db = QtGui.qApp.db
            table = db.table('rbPrintTemplate')
            where = [
                table['context'].inlist(context),
                table['deleted'].eq(0)
            ]
            for record in db.getRecordList(table, 'name, id, dpdAgreement, banUnkeptDate, groupName', where=where,
                                           order='code, name, id'):
                name = forceString(record.value('name'))
                id = forceInt(record.value('id'))
                dpdAgreement = forceInt(record.value('dpdAgreement'))
                banUnkeptDate = forceInt(record.value('banUnkeptDate'))
                groupName = forceString(record.value('groupName'))
                tup = (name, id, dpdAgreement, banUnkeptDate, groupName)
                result.append(tup)
            cls.connect()
            cls.mapTableToData[context] = result
        return result


    @classmethod
    def reset(cls):
        cls.mapTableToData.clear()

    @classmethod
    def purge(cls):
        cls.reset()


def getPrintTemplates(context):
    u"""Returns array of print templates of context.
    Context may be list of contexts.
    Print template is: (name, id, dpdAgreement)."""
    result = []
    if context:
        if not isinstance(context, list):
            context = [context]
        try:
            result = CPrintTemplatesDataCache.getData(context)
        except:
            QtGui.qApp.logCurrentException()
    return result


def getFirstPrintTemplate(context):
    templates = getPrintTemplates(context)
    if templates:
        return templates[0]
    return None


def getPrintAction(parent, context, name=u'Печать', setShortcut=True):
    result = CPrintAction(name, None, None, parent)
    result.setContext(context, setShortcut)
    return result


def getPrintButton(parent, context='', name=u'Печать'):
    result = CPrintButton(parent, name, None)
    customizePrintButton(result, context)
    return result


def customizePrintButton(btn, context, isDirty = False):
    u"""Set actions to btn: printing templates of context (or of list of contexts)"""
    templates = getPrintTemplates(context)
    if not templates:
        btn.setId(None)
        btn.setEnabled(False)
        btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
    elif len(templates) == 1:
        btn.setId(templates[0][1])
        btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
        btn.setEnabled(not(templates[0][3] == 1 and isDirty))
    else:
        btn.setId(None)
        btn.setEnabled(True)
        for i, template in enumerate(templates):
            action = CPrintAction(template[0], template[1], btn, btn)
            if template[4]:
                btn.addAction(action, template[4])
            else:
                btn.addAction(action)
            if i == 0:
                action.setShortcut(QtGui.QKeySequence(Qt.Key_F6))       #btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
            if template[3] == 1 and isDirty:
                action.setEnabled(False)
        btn.setShortcut(QtGui.QKeySequence(Qt.ALT+Qt.Key_F6))


# todo: ликвидировать!
# у нас уже есть возможность создать action печати
# и всегда была возможность навесить на кнопку произвольный список действий.
# ergo: дополнительная кастомизация кнопки печати не нужна!
# ещё раз скажу: кнопка, которая кроме печати по заданному контексту позволяет делать ещё кое-что
# называется не "навороченная-кнопка-печати-с-блекджеком-и-шлюхами" а просто кнопка,
# не которую всегда можно было "повесить" хоть список произвольных действий, хоть развесистую менюшку...

def additionalCustomizePrintButton(parent, btn, context, otherActions=None):
    #u"""Add new btn actions: printing templates of context (or list of contexts) and remove some actions
    #otherActions - dictionaries for static actions from widget: {'action': action, 'slot':slot}
    #"""
    if not otherActions:
        otherActions = []
    removeAdditionalActions(parent, btn, otherActions)
    additionalActions = []
    templates = getPrintTemplates(context)
    existsBtnMenu = None
    prepareToAdditionalCustomizePrintButton(parent, btn, otherActions)
    if len(templates) > 0:
        existsBtnMenu = btn.menu()
        if existsBtnMenu and len(existsBtnMenu.actions()) > 0:
            btn.menu().addSeparator()
        if len(templates) == 1 and not existsBtnMenu:
            action = CPrintAction(templates[0][0], templates[0][1], btn, btn)
            btn.setId(templates[0][1])
            btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
            btn.setEnabled(True)
            additionalActions.append(action)
        else:
            for i, template in enumerate(templates):
                action = CPrintAction(template[0], template[1], btn, btn)
                additionalActions.append(action)
                btn.addAction(action)
                if i == 0:# and not existsBtnMenu:
                    action.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
                    #btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
                #if not existsBtnMenu:
            btn.setShortcut(QtGui.QKeySequence(Qt.ALT+Qt.Key_F6))
    btn.setAdditionalActions(additionalActions)


# todo: ликвидируйте "кнопку-печати-с-блекджеком-и-шлюхами"
def prepareToAdditionalCustomizePrintButton(parent, btn, otherActions=None):
    if not otherActions:
        otherActions = []
    if btn.isEnabled() and not btn.menu():
        if otherActions and len(otherActions)==1:
            action = otherActions[0]
            parent.disconnect(btn, SIGNAL('clicked()'), action['slot'])
            btn.addAction(action['action'])
            parent.connect(action['action'], SIGNAL('triggered()'), action['slot'])
        else:
            actionId = btn.id
            btn.setId(None)
            db = QtGui.qApp.db
            table = db.table('rbPrintTemplate')
            where = [
                db.mainTable(table).idField().eq(actionId),
                table['deleted'].eq(0)
            ]
            record = db.getRecordEx(table, cols='name, id, dpdAgreement', where=where)
            if record:
                name = forceString(record.value('name'))
                id = forceInt(record.value('id'))
                dpdAgreement = forceInt(record.value('dpdAgreement'))
                action = CPrintAction(name, id, btn, btn)
                btn.addAction(action)
    else:
        btn.setEnabled(True)
        for action in otherActions:
            parent.connect(action['action'], SIGNAL('triggered()'), action['slot'])


# todo: ликвидируйте "кнопку-печати-с-блекджеком-и-шлюхами"
def removeAdditionalActions(parent, btn, otherActions):
    btnMenu = btn.menu()
    additionalActions = btn.popAdditionalActions()
    if btnMenu:
        for action in otherActions:
            parent.disconnect(action['action'], SIGNAL('triggered()'), action['slot'])
        for action in additionalActions:
            btnMenu.removeAction(action)
        for action in btnMenu.actions():
            if not forceStringEx(action.text()):
                btnMenu.removeAction(action)
        actionList = btnMenu.actions()
        if len(actionList) == 1:
            btn.setId(None)
            if otherActions and len(otherActions) == 1:
                parent.connect(btn, SIGNAL('clicked()'), otherActions[0]['slot'])
            else:
                action = actionList[0]
                btn.setId(action.id)
                btn.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
        elif len(actionList) == 0:
            btn.setMenu(None)
            btn.setId(None)
            btn.setEnabled(False)
    else:
        if btn.isEnabled() and len(additionalActions) == 1:
            id = btn.id
            actionId = additionalActions[0].id
            if id == actionId:
                btn.setId(None)
                btn.setEnabled(False)


# todo: ликвидируйте "кнопку-печати-с-блекджеком-и-шлюхами"
def getPrintButtonWithOtherActions(parent, context, name=u'Печать', otherActions=None):
    if not otherActions:
        otherActions = []
    assert bool(context), 'need valid context'
    assert bool(otherActions),  'need set other actions'
    templates = getPrintTemplates(context)
    actionsCount = len(otherActions)
    if not templates:
        if actionsCount > 1:
            btn = CPrintButton(parent, name, None)
            btn.setId(None)
            btn.setEnabled(True)
            for action in otherActions:
                btn.addAction(action['action'])
                parent.connect(action['action'], SIGNAL('triggered()'), action['slot'])
        else:
            btn = CPrintButton(parent, name, None)
            if actionsCount == 1:
                btn.setEnabled(True)
                action = otherActions[0]
                parent.connect(btn, SIGNAL('clicked()'), action['slot'])
            else:
                btn.setEnabled(False)
    else:
        btn = CPrintButton(parent, name, None)
        btn.setId(None)
        btn.setEnabled(True)
        for i, template in enumerate(templates):
            action = CPrintAction(template[0], template[1], btn, btn)
            btn.addAction(action)
            if i == 0:
                action.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
        for action in otherActions:
            btn.addAction(action['action'])
            parent.connect(action['action'], SIGNAL('triggered()'), action['slot'])
        btn.setShortcut(QtGui.QKeySequence(Qt.ALT+Qt.Key_F6))
    return btn


def getTemplate(templateId):
    u"""Возвращает код шаблона печати и код типа содержимого (html/exaro/svg)."""
    table = QtGui.qApp.db.table('rbPrintTemplate')
    where = [
                QtGui.qApp.db.mainTable(table).idField().eq(templateId),
                table['deleted'].eq(0)
            ]
    record = QtGui.qApp.db.getRecordEx(table=table, cols='*', where=where)
    name = forceString(record.value('name'))
    fileName = forceString(record.value('fileName'))
    content = None
    if fileName:
        fullPath = os.path.join(QtGui.qApp.getTemplateDir(), fileName)
        if os.path.isfile(fullPath):
            for enc in ('utf-8', 'cp1251'):
                try:
                    file = codecs.open(fullPath, encoding=enc, mode='r')
                    content = file.read()
                    break
                except:
                    pass

    if not content:
        content = forceString(record.value('default'))
    type = forceInt(record.value('type'))

    if not content:
        content = u'<HTML><BODY>шаблон документа пуст или испорчен</BODY></HTML>'
        type = htmlTemplate
    return name, content, type


def escape(s):
    return unicode(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace('\'', '&#39;')


def escapenl(s):
    return escape(s).replace('\n', '<BR/>')


def escapepar(s):
    parBegin = '<P style="text-indent:20px">'
    parEnd = '</P>'
    return parBegin + escape(s).replace('\n', parEnd+parBegin)+parEnd


def escapesp(s):
    return escape(s).replace(' ', '&nbsp;')


def compileTemplate(template):
    # result is tuple (complied_code, source_code)
    parser = CTemplateParser(template)
    try:
        return parser.compileToCode()
    except:
        QtGui.qApp.logCurrentException()
        raise


def execTemplate(code, data, pageFormat=None):
    # code is tuple (complied_code, source_code)
    if not pageFormat:
        pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
    try:
        infoContext = None
        for item in data.itervalues():
            if isinstance(item, CInfo):
                infoContext = item.context
                if infoContext:
                    break
        if not infoContext:
            infoContext = CInfoContext()

        stream = StringIO.StringIO()
        canvases = {}
        try:
            execContext = CTemplateContext(data, infoContext, stream, pageFormat)
            if QtGui.qApp.preferences.appPrefs.get('templateDebug', False):
                import pdb
                pdb.runeval(code[0], execContext, execContext.locals)
            sys.stdout = stream
            exec code[0] in execContext.locals, execContext
            canvases = execContext.getCanvases()
        finally:
            sys.stdout = sys.__stdout__
        return stream.getvalue(), canvases
    except ExTemplateContext, ex:
        QtGui.QMessageBox.critical(None,  u'Печатная форма',
            ex.getRusMessage(),
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        QtGui.qApp.logCurrentException()
        raise
    except Exception:
        QtGui.qApp.log('Template code failed', code[1])
        QtGui.qApp.logCurrentException()
        raise


def compileAndExecTemplate(template, data, pageFormat=None):
    # u"""Заполняет шаблон печати данными и возвращает готовый код HTML/XML"""
        return execTemplate(compileTemplate(template), data, pageFormat)


def applyTemplate(widget, templateId, data):
    # u'''Выводит на печать шаблон печати номер templateId с данными data'''
    name, template, templateType = getTemplate(templateId)
    applyTemplateInt(widget, name, template, data, templateType)


def applyTemplateInt(widget, name, template, data, templateType=htmlTemplate):
    # u'''Выводит на печать шаблон печати по имени name с кодом template и данными data'''
    pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)

    if templateType == exaroTemplate and not exaroSupport:
        content, canvases, templateType = exaroFallback()
    else:
        content, canvases = compileAndExecTemplate(template, data, pageFormat)

    if templateType == exaroTemplate:
        printExaroTemplate(content, None, True)
    elif templateType == svgTemplate:
        showSVG(widget, name, content, pageFormat)
    else:
        showHtml(widget, name, content, canvases, pageFormat)

# ###

def applyTemplateList(widget, templateId, dataList):
    name, template, templateType = getTemplate(templateId)
    applyTemplateListInt(widget, name, template, dataList, templateType)


def applyTemplateListInt(widget, name, template, dataList, templateType=htmlTemplate):
    pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)

    if templateType == exaroTemplate and not exaroSupport:
        content, canvases, templateType = exaroFallback()
    else:
        code = compileTemplate(template)
        content = u''
        canvases = {}
        for idx, data in enumerate(dataList):
            if idx > 0:
                content += '<BR clear=all style=\'page-break-before:always\'>'
            partContent, partCanvases = execTemplate(code, data, pageFormat)
            content += partContent
            canvases.update(partCanvases)

    if templateType == exaroTemplate:
        printExaroTemplate(content, None, True)
    elif templateType == svgTemplate:
        showSVG(widget, name, content, pageFormat)
    else:
        showHtml(widget, name, content, canvases, pageFormat)

def applyMultiTemplateList(widget, templateIdList, dataList):
    u"""Работает только с шаблонами типа Html"""
    nameList = []
    templateList = []
    for templateId in templateIdList:
        name, template, templateType = getTemplate(templateId)
        if templateType == htmlTemplate:
            nameList.append(name)
            templateList.append(template)
    applyMultiTemplateListInt(widget, nameList, templateList, dataList, htmlTemplate)


def applyMultiTemplateListInt(widget, nameList, templateList, dataList, templateType=htmlTemplate):
    u"""Работает только с шаблонами типа Html"""
    pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
    if not nameList:
        content, canvases, templateType = emptyTemplateList()
    else:
        content = u''
        canvases = {}
        for i in range(len(nameList)):
            name = nameList[i]
            template = templateList[i]
            data = dataList[i]
            code = compileTemplate(template)
            partContent, partCanvases = execTemplate(code, data, pageFormat)
            content += partContent
            canvases.update(partCanvases)

    if templateType == exaroTemplate:
        printExaroTemplate(content, None, True)
    else:
        showHtml(widget, name, content, canvases, pageFormat)

def showHtml(widget, name, content, canvases, pageFormat):
    reportView = CReportViewDialog(widget)
    reportView.setWindowTitle(name)
    reportView.setText(content)
    reportView.setCanvases(canvases)
    reportView.setPageFormat(pageFormat)
    reportView.exec_()



# ###

def directPrintTemplate(templateId, data, printer):
    name, template, templateType = getTemplate(templateId)
    directPrintTemplateInt(name, template, data, printer, templateType)


def directPrintTemplateInt(name, template, data, printer, templateType=htmlTemplate):
    pageFormat = CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Portrait, leftMargin=5, topMargin=5, rightMargin=5,  bottomMargin=5)
    pageFormat.setupPrinter(printer)

    if templateType == exaroTemplate and not exaroSupport:
        content, canvases, templateType = exaroFallback()
    else:
        content, canvases = compileAndExecTemplate(template, data, pageFormat)

    if templateType == exaroTemplate:
        printExaroTemplate(content, printer, False)
    elif templateType == svgTemplate:
        printSVG(name, content, printer)
    else:
        document = CTextDocument()
        document.setDefaultFont(QtGui.qApp.defaultPrintFont())
        document.setHtml(content)
        document.setCanvases(canvases)
        printTextDocument(document, name, pageFormat, printer)


def printExaroTemplate(code, printer, showPreview):
#    u'Выводит на печать шаблон Exaro'
    report = exaro.Report.ReportEngine(QtGui.qApp)
    template = report.loadReportFromString(code.replace('\\{', '{').replace('\\}', '}'))
    if template:
        template.setShowSplashScreen(False)
        template.setShowExitConfirm(False)
        template.setShowPrintPreview(showPreview)
        template.setDatabase(QtGui.qApp.db.db)
        if printer:
            template.setPrinterName(printer)
        template.exec_()
    else:
        QtGui.QMessageBox.critical(None,  u'Внимание!',
            u'Невозможно сформировать отчет Exaro.',
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)


def exaroFallback():
    return (u'<HTML><BODY>Поддержка отчетов в формате Exaro отключена. (%s)</BODY></HTML>' % exaroSupportError,
            {},
            htmlTemplate)

def emptyTemplateList():
    return (u'<HTML><BODY>Нет подходящего шаблона для вывода</BODY></HTML>',
            {},
            htmlTemplate)

class CPrintAction(QtGui.QAction):
    __pyqtSignals__ = ('printByTemplate(int)',
                      )
    def __init__(self, name, id, emitter, parent):
        QtGui.QAction.__init__(self, name, parent)
        self.id = id
        self.emitter = emitter
        # Флаг смены состояния согласия/несогласия пациентом на обработку его персональных данных
        # 0/None - при печати шаблона не менять
        # 1 - при печати шаблона менять идентификатор ДПД на "Да"
        # 1 - при печати шаблона менять идентификатор ДПД на "Нет"
        self.dpdAgreement = None
        self.context = None
        self.connect(self, SIGNAL('triggered()'), self.onTriggered)
        self._menu = None
        self.isNotEmpty = True


    def setEnabled(self, isEnabled):
        QtGui.QAction.setEnabled(self, isEnabled and self.isNotEmpty)


    def getMenu(self):
        if self._menu is None:
            self._menu = QtGui.QMenu(self.parentWidget())
        self.setMenu(self._menu)
        return self._menu


    def setContext(self, context, setShortcut=True):
        if self.context != context:
            templates = getPrintTemplates(context)
            self.isNotEmpty = bool(templates)
            if not templates:
                self.id = None
                self.setMenu(None)
                self.setEnabled(False)
                if setShortcut:
                    self.setShortcut(QtGui.QKeySequence())
            elif len(templates) == 1:
                self.id = templates[0][1]
                self.setMenu(None)
                self.setDpdAgreement(templates[0][2])
                self.setEnabled(True)
                if setShortcut:
                    self.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
            else:
                self.id = None
                menu = self.getMenu()
                menu.clear()
                for i, template in enumerate(templates):
                    action = CPrintAction(template[0], template[1], self, menu)
                    action.setDpdAgreement(template[2])
                    menu.addAction(action)
                    if setShortcut and i == 0:
                        action.setShortcut(QtGui.QKeySequence(Qt.Key_F6))
                self.setMenu(menu)
                self.setEnabled(True)
        self.context = context


    def setDpdAgreement(self, dpdAgreement):
        self.dpdAgreement = dpdAgreement


    def onTriggered(self):
        if self.dpdAgreement:
            self.changeClientDpdAgreement(QtGui.qApp.currentClientId())
        if self.id:
            db = QtGui.qApp.db
            record = db.getRecordEx('rbPrintTemplate', 'isPatientAgreed', 'id = %s' % self.id)
            if record.value('isPatientAgreed') == 1:
                if QtGui.QMessageBox.question(None, u'Подтверждение печати',
                                              u'Согласовано с пациентом?',
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No
                                              ) == QtGui.QMessageBox.Yes:
                    table = db.table('AgreementPatientPrints')
                    rec = table.newRecord()
                    rec.setValue('person_id', QtGui.qApp.userId)
                    rec.setValue('client_id', QtGui.qApp.currentClientId())
                    rec.setValue('dateTime', QtCore.QDateTime.currentDateTime())
                    rec.setValue('template_id', self.id)
                    db.insertRecord(table, rec)
            emitter = self.emitter or self
            emitter.emit(SIGNAL('printByTemplate(int)'), self.id)


    def changeClientDpdAgreement(self, clientId):
        if not clientId:
            return
        db = QtGui.qApp.db
        dpdAccountingSystemId = forceRef(db.translate('rbAccountingSystem', 'code', u'ДПД', 'id'))
        record = db.getRecordEx('ClientIdentification', '*', 'deleted=0 AND accountingSystem_id=%d AND client_id=%d'%(dpdAccountingSystemId, clientId))
        if not record:
            record = db.table('ClientIdentification').newRecord()
            record.setValue('accountingSystem_id', QVariant(dpdAccountingSystemId))
            record.setValue('client_id', QVariant(clientId))
        value = u'Да' if self.dpdAgreement == 1 else u'Нет'
        record.setValue('identifier', QVariant(value))
        record.setValue('checkDate', QVariant(QDate.currentDate()))
        db.insertOrUpdate('ClientIdentification', record)


class CPrintButton(QtGui.QPushButton):
    __pyqtSignals__ = ('printByTemplate(int)',
                      )

    def __init__(self, parent, name='', id=None):
        QtGui.QPushButton.__init__(self, name, parent)
        self.setId(id)
        self.connect(self, SIGNAL('clicked()'), self.onClicked)
        self._additionalActions = []
        self.groups = {}


    def additionalActions(self):
        return self._additionalActions


    def popAdditionalActions(self):
        result = self._additionalActions
        self._additionalActions = []
        return result


    def setAdditionalActions(self, additionalActions=None):
        if not additionalActions:
            additionalActions = []
        self._additionalActions = additionalActions


    def setId(self, id):
        self.id = id
        self.actions = []
        self.groups = {}
        self._additionalActions = []
        self.setMenu(None)


    def addAction(self, action, groupName = None):
        menu = self.menu()
        if not menu:
            menu = QtGui.QMenu(self)
            self.setMenu(menu)
        self.actions.append(action)
        if groupName and not groupName in self.groups:
            subMenu = menu.addMenu(groupName)
            subMenu.addAction(action)
            self.groups[groupName] = subMenu
        elif groupName:
            subMenu = self.groups[groupName]
            subMenu.addAction(action)
        else:
            menu.addAction(action)


    def onClicked(self):
        if self.id:
            self.emit(SIGNAL('printByTemplate(int)'), self.id)


# ################################################


class CTemplateParser(object):
    def __init__(self, txt, filename = '<template>'):
        self.blockText = re.compile(r'''([^\\{]|\\.)*''')
        self.blockCode = re.compile(r'''\{([^\\'"}]*|('(\\.|[^'])*')|("(\\.|[^"])*"))*\}''')
        self.keywords  = [('if',   re.compile(r'''\s*if\s*:\s*''')),
                          ('elif', re.compile(r'''\s*elif\s*:\s*''')),
                          ('else', re.compile(r'''\s*else\s*:\s*''')),
                          ('end',  re.compile(r'''\s*end\s*:\s*''')),
                          ('for',  re.compile(r'''\s*for\s*:\s*''')),
                          ('def',  re.compile(r'''\s*def\s*:\s*''')),
                          ('immed',re.compile(r'''\s*:\s*''')),
                         ]
        self.pos = 0
        self.txt = txt
        self.filename = filename
        self.stream = StringIO.StringIO()


    def compileToStream(self):
        lex = self.compileInt(0, True)
        if lex:
            self.syntaxError('unexpected code', lex[1], lex[2])


#    def compileToString(self):
#        self.compileToStream()
#        return self.stream.getvalue()


    def compileToCode(self):
        self.compileToStream()
        program = self.stream.getvalue()
        return compile(program, self.filename, 'exec'), program


    def compileInt(self, indent, check):
        prefix = '    '*indent
        oldLen = self.stream.len
        while True:
            lex = self.getLex()
            if not lex:
                break;
            keyword = lex[0]
            if keyword == 'txt':
                if lex[2]:
                    print >>self.stream, prefix+'write('+repr(lex[2])+')'
            elif keyword == 'eval':
                expr = lex[2]
                if check:
                    self.checkExprSyntax(lex[1], expr)
                fmt = lex[3]
                if fmt == 'h':
                    print >>self.stream, prefix+'write('+expr+')'
                elif fmt == 'n':
                    print >>self.stream, prefix+'write(escapenl('+expr+'))'
                elif fmt == 'p':
                    print >>self.stream, prefix+'write(escapepar('+expr+'))'
                else:
                    print >>self.stream, prefix+'write(escape('+expr+'))'
            elif keyword == 'immed':
                txt = lex[2]
                if check:
                    self.checkImmedSyntax(lex[1], txt)
                print >>self.stream, prefix+txt
            elif keyword == 'for':
                startLex = lex
                txt = lex[2]
                if check:
                    self.checkForSyntax(lex[1], txt)
                print >>self.stream, prefix+'for '+txt+':'
                lex = self.compileInt(indent+1, check)
                if not lex:
                    self.syntaxError('for not closed', startLex[1], startLex[2])
                elif lex[0] != 'end':
                    self.syntaxError('unexpected code', lex[1], lex[2])
            elif keyword == 'if':
                startLex = lex
                if check:
                    self.checkExprSyntax(lex[1], lex[2])
                print >>self.stream, prefix+'if '+lex[2]+':'
                lex = self.compileInt(indent+1, check)
                while lex and lex[0] == 'elif':
                    startLex = lex
                    if check:
                        self.checkExprSyntax(lex[1], lex[2])
                    print >>self.stream, prefix+'elif '+lex[2]+':'
                    lex = self.compileInt(indent+1, check)
                if lex and lex[0] == 'else':
                    startLex = lex
                    print >>self.stream, prefix+'else:'
                    lex = self.compileInt(indent+1, check)
                if not lex:
                    self.syntaxError(startLex[0]+' not closed', startLex[1], startLex[2])
                elif lex[0] != 'end':
                    self.syntaxError('unexpected code', lex[1], lex[2])
            elif keyword == 'def':
                startLex = lex
                start = lex[1], self.stream.tell()
                print >>self.stream, prefix+'def '+lex[2]+':'
                lex = self.compileInt(indent+1, False)
                if not lex:
                    self.syntaxError('def not closed', startLex[1], startLex[2])
                elif lex[0] != 'end':
                    self.syntaxError('unexpected code', lex[1], lex[2])
                self.checkImmedSyntax(start[0], self.stream.getvalue()[start[1]:])
            else:
                break
        if oldLen == self.stream.len:
            print >>self.stream, prefix+'pass'
        return lex


    def checkExprSyntax(self, loc, expr):
        try:
            code = 'if '+expr+' :\n    pass\n'
            compile(code,'<string>','exec')
            return
        except SyntaxError, err:
            self.syntaxError(err.msg, loc, expr)


    def checkImmedSyntax(self, loc, expr):
        try:
            code = expr+'\n'
            compile(code,'<string>','exec')
            return
        except SyntaxError, err:
            self.syntaxError(err.msg, loc, expr)


    def checkForSyntax(self, loc, expr):
        try:
            code = 'for '+expr+' :\n    pass\n'
            compile(code,'<string>','exec')
            return
        except SyntaxError, err:
            self.syntaxError(err.msg, loc, expr)


    def syntaxError(self, msg, offset, code):
        lineno = self.txt[:offset].count('\n')
        pos = -1
        for i in xrange(lineno):
            pos = self.txt.find('\n', pos+1)
        raise SyntaxError(msg, (self.filename, lineno+1, offset-pos-1, code if len(code)<48 else code[:48]+'...'))


    def getLex(self):
        if len(self.txt) == self.pos:
            return None
        elif self.txt[self.pos:self.pos+1] != '{':
            m = self.blockText.match(self.txt,self.pos)
            if m:
                self.pos = m.end()
                return ('txt', m.start(), self.txt[m.start(): m.end()]) # здесь stip не ставить, иначе ломаются шаблоны Exaro
        else:
            m = self.blockCode.match(self.txt,self.pos)
            if m:
                self.pos = m.end()
                for keyword, keywordre in self.keywords:
                    m2 = keywordre.match(self.txt, m.start()+1)
                    if m2:
                        return (keyword, m.start(), self.txt[m2.end():m.end()-1])
                txt = self.txt[m.start()+1: m.end()-1]
                fmt = ''
                pos = txt.rfind(':')
                if pos>=0 :
                    fmt = txt[pos+1:].strip()
                    if fmt in ('h','u','n','p',''):
                        txt = txt[:pos]
                        if fmt == 'u':
                            fmt = 'h'
                    else:
                        fmt = ''
                return ('eval', m.start(), txt.lstrip(), fmt)
        self.syntaxError('bad block syntax', self.pos, self.txt[self.pos:])


# ####################################


class CDictProxy(object):
    def __init__(self, path, data):
        object.__setattr__(self, 'path', path)
        object.__setattr__(self, 'data', data)

    def __getattr__(self, name):
        if self.data.has_key(name):
            result = self.data[name]
            if type(result) == dict:
                return CDictProxy(self.path+'.'+name, result)
            else:
                return result
        else:
            s = self.path+'.'+name
            QtGui.qApp.log(u'Ошибка при печати шаблона',
                           u'Переменная или функция "%s" не определена.\nвозвращается None'%s)
            return None

    def __setattr__(self, name, value):
        self.data[name] = value

    def __len__(self):
        return len(self.data)


# ####################################


class CCanvas(object):
    black   = QtGui.QColor(  0,   0,   0)
    red     = QtGui.QColor(255,   0,   0)
    green   = QtGui.QColor(  0, 255,   0)
    yellow  = QtGui.QColor(255, 255,   0)
    blue    = QtGui.QColor(  0,   0, 255)
    magenta = QtGui.QColor(255,   0, 255)
    cyan    = QtGui.QColor(  0, 255, 255)
    white   = QtGui.QColor(255, 255, 255)

    def __init__(self, width, height):
        self.image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
        self.penColor = CCanvas.black
        self.brushColor = CCanvas.red
        self.fill(CCanvas.white)


    @staticmethod
    def rgb(self, r, g, b):
        return QtGui.QColor(r, g, b)


    def setPen(self, color):
        self.penColor = color


    def setBrush(self, color):
        self.brushColor = color


    def fill(self, color):
        painter = QtGui.QPainter(self.image)
        painter.fillRect(self.image.rect(), QtGui.QBrush(color))
        painter.end()


    def line(self, x1, y1, x2, y2):
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(self.penColor))
        painter.drawLine(x1, y1, x2, y2)
        painter.end()


    def ellipse(self, x, y, w, h):
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(self.penColor))
        painter.setBrush(QtGui.QBrush(self.brushColor))
        painter.drawEllipse(x, y, w, h)
        painter.end()


# ####################################

class ExTemplateContext(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Template context error")
        self._rusText = u"Ошибка в данных печатной формы. %s"%text

    def getRusMessage(self):
        return self._rusText


class CTemplateContext(dict):
    def __init__(self, data, infoContext, stream, pageFormat=None):
        self.data = data
        now = QDateTime.currentDateTime()
        builtins = {
                 'escape'              : escape,
                 'escapenl'            : escapenl,
                 'escapepar'           : escapepar,
                 'escapesp'            : escapesp,
                 'currentDate'         : CDateInfo(now.date()),
                 'currentTime'         : CTimeInfo(now.time()),
                 'currentOrganisation' : infoContext.getInstance(COrgInfo, QtGui.qApp.currentOrgId()),
                 'currentOrgStructure' : infoContext.getInstance(COrgStructureInfo, QtGui.qApp.currentOrgStructureId()),
                 'currentPerson'       : infoContext.getInstance(CPersonInfo,  QtGui.qApp.userId),
                 'present'             : self.present,
                 'pdf417'              : self.pdf417,
                 'code128'             : code128,
                 'getActionBarCode'    : self.getActionBarCode,
                 'p38code'             : self.p38code,
                 'p38test'             : self.p38test,
                 'amountToWords'       : self.amountToWords,
                 'Canvas'              : CCanvas,
                 'dialogs'             : infoContext.getInstance(CDialogsInfo),
                 'write'               : lambda string: "" if stream.write(forceString(string)) else "",
                 'error'               : self.error
               }
        for expr in PrintHelpers.__all__:
            builtins[expr] = PrintHelpers.__dict__[expr]
        if pageFormat:
            builtins['setPageSize'] = pageFormat.setPageSize
            builtins['setOrientation'] = pageFormat.setOrientation
            builtins['setPageOrientation'] = pageFormat.setOrientation
            builtins['setMargins'] = pageFormat.setMargins
            builtins['setLeftMargin'] = pageFormat.setLeftMargin
            builtins['setTopMargin'] = pageFormat.setTopMargin
            builtins['setRightMargin'] = pageFormat.setRightMargin
            builtins['setBottomMargin'] = pageFormat.setBottomMargin
        self.locals = {}
        self.locals.update(data)
        self.locals.update(builtins)
        self.globals = {}
        self.globals.update(self.locals)


    def __getitem__(self, key):
        if self.locals.has_key(key):
            result = self.locals[key]
        elif self.globals.has_key(key):
            result = self.globals[key]
        elif __builtins__.has_key(key):
            result = __builtins__[key]
        else:
            QtGui.qApp.log(u'Ошибка при печати шаблона',
                           u'Переменная или функция "%s" не определена.\nвозвращается None'%key)
            result = None

        if type(result) == dict:
            return CDictProxy(key, result)
        else:
            return result


    def __setitem__(self, key, value):
        if type(value) == CDictProxy:
            self.locals[key] = value.data
        else:
            self.locals[key] = value


    def __delitem__(self, key):
        del self.locals[key]


    def present(self, key):
        seq = key.split('.')
        key = seq[0]
        if self.locals.has_key(key):
            data = self.locals[key]
        elif self.globals.has_key(key):
            data = self.globals[key]
        elif __builtins__.has_key(key):
            data = __builtins__[key]
        else:
            return False
        for name in seq[1:]:
            if hasattr(data, 'has_key') and data.has_key(name):
                data = data[name]
            else:
                return False
        return True


    def getCanvases(self):
        result = {}
        for key, val in self.locals.iteritems():
            if isinstance(val, CCanvas):
                result[key] = val
        return result


    def pdf417(self, data, **params):
        params['data'] = data
        url = 'pdf417://localhost?'+urlencode(params)
        return '<IMG SRC="'+url+'">'

    @staticmethod
    def getActionBarCode(actionId, amount):
        return str(actionId) + '+' + str(amount)

    @classmethod
    def p38test(cls):
        return cls.p38code('1027802751701', '1357', '41043', '4008', '4104300000002535', 'I67', '1', 100, 1, '3780115', u'4.5+80 мкг+мкг/доза', 1.234, u'008-656-445 65', '083', '1', QDate(2008, 3, 25))

    @staticmethod
    def p38code(OGRN, doctorCode, orgCode, series, number, MKB, fundingCode, benefitPersent, isIUN, remedyCode, remedyDosage, remedyQuantity, SNILS, personBenefitCategory, periodOfValidity, date, isVK=0):
        def intToBits(data, bitsWidth):
            if isinstance(data,(int, long)):
                n = data
            elif not data:
                n = 0
            else:
                try:
                    n = int(data, 10)
                except:
                    n = 0
            result = format(n,'b')
            result = result.rjust(bitsWidth,'0') if len(result)<=bitsWidth else result[:bitsWidth]
            return result

        def strToBits(data, strWidth):
            s = unicode(data).encode('cp1251')
            s = s.ljust(strWidth,' ') if len(s)<=strWidth else s[:strWidth]
            result = ''.join(format(ord(c), '>08b') for c in s)
            return result

        def bitsToChars(bits):
            result = ''
            for i in xrange(0, len(bits), 8):
                result += chr(int(bits[i:i+8], 2))
            return result

        bits = intToBits(OGRN, 50) + \
               strToBits(doctorCode, 7) + \
               intToBits(OGRN, 50) + \
               strToBits(orgCode,  7) + \
               strToBits(series,  14) + \
               intToBits(number, 64) + \
               strToBits(MKB, 7) + \
               intToBits(fundingCode, 2) + \
               ('0' if benefitPersent == 100 else '1') + \
               ('1' if isIUN else '0') + \
               intToBits(remedyCode, 44) + \
               intToBits(unformatSNILS(SNILS), 37) + \
               strToBits(remedyDosage, 20) + \
               intToBits(int(remedyQuantity*1000), 24) + \
               intToBits(personBenefitCategory, 10) + \
               ('1' if periodOfValidity else '0') + \
               intToBits(date.year()-2000, 7) + \
               intToBits(date.month(), 4) + \
               intToBits(date.day(), 5)
        bits += '1' if isVK else '0' # признак наличия ВК
        bits += '0'*(-len(bits)%8)
        bits += intToBits(6, 8) # версия протокола
        chars = bitsToChars(bits)
        resultCode = b64encode(chars)
        return 'p' + resultCode
#
#

    @staticmethod
    def p38decode(code):
        result = {}
        chars = b64decode(code[1:])
        bits = ''.join(['{:08b}'.format(ord(c)) for c in chars])

        bitsToInt = lambda b: int(b, 2)
        bitsToString = lambda b: ''.join([chr(int(b[i:i+8], 2)) for i in xrange(0, len(b), 8)]).decode('cp1251')

        mask = [('OGRN', 50, bitsToInt),
                ('doctorCode', 7*8, bitsToString),
                ('OGRN', 50, bitsToInt),
                ('orgCode', 7*8, bitsToString),
                ('series', 14*8, bitsToString),
                ('number', 64, bitsToInt),
                ('mkb', 7*8, bitsToString),
                ('fundingCode', 2, bitsToInt),
                ('benefitPersent', 1, lambda x: x),
                ('isIUN', 1, lambda x: x),
                ('remedyCode', 44, bitsToInt),
                ('SNILS', 37, lambda b: str(bitsToInt(b)).rjust(11, '0')),
                ('remedyDosage', 20*8, bitsToString),
                ('remedyQuantity', 24, bitsToInt),
                ('personBenefitCategory', 10, bitsToInt),
                ('periodOfValidity', 1, lambda x: x),
                ('year', 7, bitsToInt),
                ('month', 4, bitsToInt),
                ('day', 5, bitsToInt),
                ('isVK', 1, lambda x: x)]


        start = 0
        for name, offset, l in mask:
            result[name] = l(bits[start:start+offset])
            start += offset

        return result


    def amountToWords(self, num, currency=currencyRUR):
        return amountToWords(num, currency)


    def error(self, text):
        raise ExTemplateContext(text)



if __name__ == '__main__':
    code = 'pADuBhZRajEzNSAgICAAO4GFlFqMzIwMDEgIDAzLTE1LTMxICAgICAgAAAAAAAehatSNTIuMCAgQAAAAAGoCtR+UZGpgQdnGX9nWQGRB2dZAQEBAQEBAAJxAKQedwBg=='
    print '\n'.join(['% 20s: %s' % (k, v) for k, v in CTemplateContext.p38decode(code).iteritems()])

    f = CTemplateContext.pdf417(CTemplateContext.p38test(), {})

    sys.exit(0)

    app = QtGui.QApplication(sys.argv)
    if exaroSupport:
        reportEngine = exaro.Report.ReportEngine(app)
        report = reportEngine.loadReport('report.bdrt')
        if report:
            report.setShowSplashScreen(False)
            report.exec_()
        else:
            print 'report create failed'
    else:
        print 'Exaro is not supported'
