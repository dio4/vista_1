# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportsGeneratorSetupDialog.ui'
#
# Created: Tue Nov 25 17:14:01 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ReportsGeneratorSetupDialog(object):
    def setupUi(self, ReportsGeneratorSetupDialog):
        ReportsGeneratorSetupDialog.setObjectName(_fromUtf8("ReportsGeneratorSetupDialog"))
        ReportsGeneratorSetupDialog.resize(692, 576)
        self.gridLayout_2 = QtGui.QGridLayout(ReportsGeneratorSetupDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tabWidget = QtGui.QTabWidget(ReportsGeneratorSetupDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabParameters = QtGui.QWidget()
        self.tabParameters.setObjectName(_fromUtf8("tabParameters"))
        self.gridLayout = QtGui.QGridLayout(self.tabParameters)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtInputFileName = QtGui.QLineEdit(self.tabParameters)
        self.edtInputFileName.setObjectName(_fromUtf8("edtInputFileName"))
        self.gridLayout.addWidget(self.edtInputFileName, 0, 0, 1, 1)
        self.btnBrowseInputFile = QtGui.QToolButton(self.tabParameters)
        self.btnBrowseInputFile.setObjectName(_fromUtf8("btnBrowseInputFile"))
        self.gridLayout.addWidget(self.btnBrowseInputFile, 0, 1, 1, 1)
        self.tblParameters = QtGui.QTableView(self.tabParameters)
        self.tblParameters.setObjectName(_fromUtf8("tblParameters"))
        self.tblParameters.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tblParameters, 2, 0, 1, 2)
        self.cmbTemplateFile = QtGui.QComboBox(self.tabParameters)
        self.cmbTemplateFile.setObjectName(_fromUtf8("cmbTemplateFile"))
        self.gridLayout.addWidget(self.cmbTemplateFile, 1, 0, 1, 2)
        self.tabWidget.addTab(self.tabParameters, _fromUtf8(""))
        self.tabAdditionaOptions = QtGui.QWidget()
        self.tabAdditionaOptions.setObjectName(_fromUtf8("tabAdditionaOptions"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tabAdditionaOptions)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gbHeaderSection = QtGui.QGroupBox(self.tabAdditionaOptions)
        self.gbHeaderSection.setCheckable(True)
        self.gbHeaderSection.setObjectName(_fromUtf8("gbHeaderSection"))
        self.gridLayout_8 = QtGui.QGridLayout(self.gbHeaderSection)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.spbHeaderColumnCount = QtGui.QSpinBox(self.gbHeaderSection)
        self.spbHeaderColumnCount.setMinimum(1)
        self.spbHeaderColumnCount.setMaximum(8)
        self.spbHeaderColumnCount.setObjectName(_fromUtf8("spbHeaderColumnCount"))
        self.gridLayout_8.addWidget(self.spbHeaderColumnCount, 4, 1, 1, 1)
        self.spbHeaderRowCount = QtGui.QSpinBox(self.gbHeaderSection)
        self.spbHeaderRowCount.setMinimum(1)
        self.spbHeaderRowCount.setMaximum(8)
        self.spbHeaderRowCount.setObjectName(_fromUtf8("spbHeaderRowCount"))
        self.gridLayout_8.addWidget(self.spbHeaderRowCount, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_8.addItem(spacerItem, 6, 1, 1, 1)
        self.tedtHeaderSection = QtGui.QTextEdit(self.gbHeaderSection)
        self.tedtHeaderSection.setObjectName(_fromUtf8("tedtHeaderSection"))
        self.gridLayout_8.addWidget(self.tedtHeaderSection, 1, 0, 6, 1)
        self.lblHeaderRowCount = QtGui.QLabel(self.gbHeaderSection)
        self.lblHeaderRowCount.setObjectName(_fromUtf8("lblHeaderRowCount"))
        self.gridLayout_8.addWidget(self.lblHeaderRowCount, 1, 1, 1, 1)
        self.lblHeaderColumnCount = QtGui.QLabel(self.gbHeaderSection)
        self.lblHeaderColumnCount.setObjectName(_fromUtf8("lblHeaderColumnCount"))
        self.gridLayout_8.addWidget(self.lblHeaderColumnCount, 3, 1, 1, 1)
        self.btnAddToHeader = QtGui.QPushButton(self.gbHeaderSection)
        self.btnAddToHeader.setMaximumSize(QtCore.QSize(23, 23))
        self.btnAddToHeader.setObjectName(_fromUtf8("btnAddToHeader"))
        self.gridLayout_8.addWidget(self.btnAddToHeader, 5, 1, 1, 1)
        self.gridLayout_4.addWidget(self.gbHeaderSection, 1, 0, 1, 1)
        self.gbFooterSection = QtGui.QGroupBox(self.tabAdditionaOptions)
        self.gbFooterSection.setCheckable(True)
        self.gbFooterSection.setObjectName(_fromUtf8("gbFooterSection"))
        self.gridLayout_9 = QtGui.QGridLayout(self.gbFooterSection)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.tedtFooterSection = QtGui.QTextEdit(self.gbFooterSection)
        self.tedtFooterSection.setObjectName(_fromUtf8("tedtFooterSection"))
        self.gridLayout_9.addWidget(self.tedtFooterSection, 0, 0, 6, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_9.addItem(spacerItem1, 5, 1, 1, 1)
        self.lblFooterColumnCount = QtGui.QLabel(self.gbFooterSection)
        self.lblFooterColumnCount.setObjectName(_fromUtf8("lblFooterColumnCount"))
        self.gridLayout_9.addWidget(self.lblFooterColumnCount, 2, 1, 1, 1)
        self.lblFooterRowCount = QtGui.QLabel(self.gbFooterSection)
        self.lblFooterRowCount.setObjectName(_fromUtf8("lblFooterRowCount"))
        self.gridLayout_9.addWidget(self.lblFooterRowCount, 0, 1, 1, 1)
        self.spbFooterColumnCount = QtGui.QSpinBox(self.gbFooterSection)
        self.spbFooterColumnCount.setMinimum(1)
        self.spbFooterColumnCount.setMaximum(8)
        self.spbFooterColumnCount.setObjectName(_fromUtf8("spbFooterColumnCount"))
        self.gridLayout_9.addWidget(self.spbFooterColumnCount, 3, 1, 1, 1)
        self.spbFooterRowCount = QtGui.QSpinBox(self.gbFooterSection)
        self.spbFooterRowCount.setMinimum(1)
        self.spbFooterRowCount.setMaximum(8)
        self.spbFooterRowCount.setObjectName(_fromUtf8("spbFooterRowCount"))
        self.gridLayout_9.addWidget(self.spbFooterRowCount, 1, 1, 1, 1)
        self.btnAddToFooter = QtGui.QPushButton(self.gbFooterSection)
        self.btnAddToFooter.setMaximumSize(QtCore.QSize(23, 23))
        self.btnAddToFooter.setObjectName(_fromUtf8("btnAddToFooter"))
        self.gridLayout_9.addWidget(self.btnAddToFooter, 4, 1, 1, 1)
        self.gridLayout_4.addWidget(self.gbFooterSection, 3, 0, 1, 1)
        self.gbMainTableSection = QtGui.QGroupBox(self.tabAdditionaOptions)
        self.gbMainTableSection.setEnabled(True)
        self.gbMainTableSection.setObjectName(_fromUtf8("gbMainTableSection"))
        self.gridLayout_10 = QtGui.QGridLayout(self.gbMainTableSection)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.mainTableColumns = QtGui.QTableWidget(self.gbMainTableSection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainTableColumns.sizePolicy().hasHeightForWidth())
        self.mainTableColumns.setSizePolicy(sizePolicy)
        self.mainTableColumns.setMinimumSize(QtCore.QSize(0, 0))
        self.mainTableColumns.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        self.mainTableColumns.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.mainTableColumns.setObjectName(_fromUtf8("mainTableColumns"))
        self.mainTableColumns.setColumnCount(3)
        self.mainTableColumns.setRowCount(1)
        item = QtGui.QTableWidgetItem()
        self.mainTableColumns.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.mainTableColumns.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.mainTableColumns.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.mainTableColumns.setHorizontalHeaderItem(2, item)
        self.mainTableColumns.verticalHeader().setVisible(False)
        self.gridLayout_10.addWidget(self.mainTableColumns, 1, 0, 1, 1)
        self.chkTranspose = QtGui.QCheckBox(self.gbMainTableSection)
        self.chkTranspose.setObjectName(_fromUtf8("chkTranspose"))
        self.gridLayout_10.addWidget(self.chkTranspose, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.gbMainTableSection, 2, 0, 1, 1)
        self.textAppearanceEditor = CTextAppearanceEditor(self.tabAdditionaOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textAppearanceEditor.sizePolicy().hasHeightForWidth())
        self.textAppearanceEditor.setSizePolicy(sizePolicy)
        self.textAppearanceEditor.setObjectName(_fromUtf8("textAppearanceEditor"))
        self.gridLayout_4.addWidget(self.textAppearanceEditor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabAdditionaOptions, _fromUtf8(""))
        self.tabPreview = QtGui.QWidget()
        self.tabPreview.setObjectName(_fromUtf8("tabPreview"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tabPreview)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tedtPreview = QtGui.QTextEdit(self.tabPreview)
        self.tedtPreview.setObjectName(_fromUtf8("tedtPreview"))
        self.gridLayout_3.addWidget(self.tedtPreview, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabPreview, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_6 = QtGui.QGridLayout(self.tab)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.tedtQueryStmt = QtGui.QPlainTextEdit(self.tab)
        self.tedtQueryStmt.setObjectName(_fromUtf8("tedtQueryStmt"))
        self.gridLayout_6.addWidget(self.tedtQueryStmt, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tabInfo = QtGui.QWidget()
        self.tabInfo.setObjectName(_fromUtf8("tabInfo"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tabInfo)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.tedtInfo = QtGui.QTextEdit(self.tabInfo)
        self.tedtInfo.setReadOnly(True)
        self.tedtInfo.setObjectName(_fromUtf8("tedtInfo"))
        self.gridLayout_5.addWidget(self.tedtInfo, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabInfo, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 4)
        self.btnSaveChanged = QtGui.QPushButton(ReportsGeneratorSetupDialog)
        self.btnSaveChanged.setObjectName(_fromUtf8("btnSaveChanged"))
        self.gridLayout_2.addWidget(self.btnSaveChanged, 1, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(269, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportsGeneratorSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 3, 1, 1)
        self.chkIsLandscapeOrientation = QtGui.QCheckBox(ReportsGeneratorSetupDialog)
        self.chkIsLandscapeOrientation.setObjectName(_fromUtf8("chkIsLandscapeOrientation"))
        self.gridLayout_2.addWidget(self.chkIsLandscapeOrientation, 1, 2, 1, 1)

        self.retranslateUi(ReportsGeneratorSetupDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportsGeneratorSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportsGeneratorSetupDialog.reject)
        QtCore.QObject.connect(self.gbHeaderSection, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.spbHeaderRowCount.setEnabled)
        QtCore.QObject.connect(self.gbHeaderSection, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.spbHeaderColumnCount.setEnabled)
        QtCore.QObject.connect(self.gbFooterSection, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.spbFooterRowCount.setEnabled)
        QtCore.QObject.connect(self.gbFooterSection, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.spbFooterColumnCount.setEnabled)
        QtCore.QObject.connect(self.gbHeaderSection, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.btnAddToHeader.setEnabled)
        QtCore.QObject.connect(self.gbFooterSection, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.btnAddToFooter.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportsGeneratorSetupDialog)

    def retranslateUi(self, ReportsGeneratorSetupDialog):
        ReportsGeneratorSetupDialog.setWindowTitle(_translate("ReportsGeneratorSetupDialog", "Dialog", None))
        self.btnBrowseInputFile.setText(_translate("ReportsGeneratorSetupDialog", "...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabParameters), _translate("ReportsGeneratorSetupDialog", "Параметры отчета", None))
        self.gbHeaderSection.setTitle(_translate("ReportsGeneratorSetupDialog", "Верхняя (заголовочная) секция", None))
        self.lblHeaderRowCount.setText(_translate("ReportsGeneratorSetupDialog", "строк:", None))
        self.lblHeaderColumnCount.setText(_translate("ReportsGeneratorSetupDialog", "стобцов:", None))
        self.btnAddToHeader.setText(_translate("ReportsGeneratorSetupDialog", "+", None))
        self.gbFooterSection.setTitle(_translate("ReportsGeneratorSetupDialog", "Нижняя секция", None))
        self.lblFooterColumnCount.setText(_translate("ReportsGeneratorSetupDialog", "стобцов:", None))
        self.lblFooterRowCount.setText(_translate("ReportsGeneratorSetupDialog", "строк:", None))
        self.btnAddToFooter.setText(_translate("ReportsGeneratorSetupDialog", "+", None))
        self.gbMainTableSection.setTitle(_translate("ReportsGeneratorSetupDialog", "Основная таблица", None))
        item = self.mainTableColumns.verticalHeaderItem(0)
        item.setText(_translate("ReportsGeneratorSetupDialog", "Новая строка", None))
        item = self.mainTableColumns.horizontalHeaderItem(0)
        item.setText(_translate("ReportsGeneratorSetupDialog", "Новый столбец", None))
        item = self.mainTableColumns.horizontalHeaderItem(1)
        item.setText(_translate("ReportsGeneratorSetupDialog", "Новый столбец", None))
        item = self.mainTableColumns.horizontalHeaderItem(2)
        item.setText(_translate("ReportsGeneratorSetupDialog", "Новый столбец", None))
        self.chkTranspose.setText(_translate("ReportsGeneratorSetupDialog", "Развернуть на 90 градусов против часовой стрелки", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAdditionaOptions), _translate("ReportsGeneratorSetupDialog", "Дополнительные настройки", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPreview), _translate("ReportsGeneratorSetupDialog", "Предпросмотр", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ReportsGeneratorSetupDialog", "Текст запроса", None))
        self.tedtInfo.setHtml(_translate("ReportsGeneratorSetupDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Общие положения</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Входной файл (далее &quot;</span><span style=\" font-size:8pt; font-weight:600;\">шаблон отчета</span><span style=\" font-size:8pt;\">&quot;) должен иметь расширение &quot;sql&quot;.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Шаблон отчета</span><span style=\" font-size:8pt;\"> может содержать: </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">текст SQL-запроса для выборки данных из базы, </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">комментарии в формате SQL, </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">настраиваемые <span style=\" font-weight:600;\">параметры отчета</span>. </li></ul>\n"
"<p style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Параметры отчета</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Параметр отчета представляет собой строку вида: {</span><span style=\" font-size:8pt; font-style:italic;\">name</span><span style=\" font-size:8pt;\">[#</span><span style=\" font-size:8pt; font-style:italic;\">n</span><span style=\" font-size:8pt;\">]@</span><span style=\" font-size:8pt; font-style:italic;\">type</span><span style=\" font-size:8pt;\">} </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">, где: </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">name</span> - имя параметра. Может содержать буквы и символы подчеркивания (последние будут заменятся на пробемы при отображении названия). </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">n</span> - сортировочный индекс. Указывает порядок вывода параметра в списке. Может быть опущен. </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">type</span> - тип параметра. Определяет используемый для редактирования элемент интерфейса.</li></ul>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:8pt;\">. </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">например, он может выглядеть так: {</span><span style=\" font-size:8pt; font-style:italic;\">Дата_рождения_пациента</span><span style=\" font-size:8pt;\">#</span><span style=\" font-size:8pt; font-style:italic;\">2@date} </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Поддерживаемые типы: </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">date</span> - для редактирования используется элемент с календарем. </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">datetime</span> - то же, что и date, но с возможностью указывать еще и время. </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">str</span> - для редактирования используется обычное поле ввода текста.</li>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:1; text-indent:0px;\"><span style=\" font-size:8pt;\">. </span></p>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">int</span> - для редактирования используется spinbox с пределами 0 - 999 и шагом 1. </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">float</span> - для редактирования используется spinbox с пределами 0.0 - 99.9 и шагом 0.1. </li></ul></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInfo), _translate("ReportsGeneratorSetupDialog", "?", None))
        self.btnSaveChanged.setText(_translate("ReportsGeneratorSetupDialog", "Сохранить изменения", None))
        self.chkIsLandscapeOrientation.setText(_translate("ReportsGeneratorSetupDialog", "Альбомная ориентация", None))

from Reports.ReportsGenerator.TextAppearanceEditor import CTextAppearanceEditor
