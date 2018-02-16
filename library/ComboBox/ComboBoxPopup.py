# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2017 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.MES.Ui_MESComboBoxPopup import Ui_MESComboBoxPopup
from library.TableModel import CSortFilterProxyTableModel, CTableModel, CTextCol
from library.Utils import forceString

__author__ = 'nat'


class CComboBoxPopup(QtGui.QFrame, Ui_MESComboBoxPopup):
    __pyqtSignals__ = (
        'ItemSelected(int)',
        'closed()'
    )

    def __init__(self, parent=None, type='MES'):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)

        self.tableModel = CPopupTableModel(self, type)
        self.filterModelProxy = CSortFilterProxyTableModel(self)
        self.filterModelProxy.setSourceModel(self.tableModel)
        self.filterModelProxy.setFilterKeyColumn(0)
        self.filterModelProxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.tableSelectionModel = QtGui.QItemSelectionModel(self.filterModelProxy, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.table.setModel(self.filterModelProxy)
        self.table.setSelectionModel(self.tableSelectionModel)
        self.connect(self.table, QtCore.SIGNAL('hide()'), self.close)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        # к сожалению в данном случае setDefault обеспечивает рамочку вокруг кнопочки
        # но enter не работает...
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setShortcut(QtCore.Qt.Key_Return)
        self._clientSex = 0
        self._clientAge = None
        self._contractId = None
        self._endDateForTariff = None
        self._mesCodeTemplate = None
        self._mesNameTemplate = None
        self._specialityId = None
        self._MKB = ''
        self._MKB2List = []
        self._id = None
        self._availableIdList = None  # atronah: None - не фильтровать по списку id. [] - фильтровать по пустому списку (т.е. запрет выбора)
        self._dicTag = None
        self.table.installEventFilter(self)
        self.on_buttonBox_reset()
        self._actionTypeIdList = None
        self._checkDate = None
        self._isDoubleClick = False

    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent != None:
            opt = QtGui.QStyleOptionComboBox()
            opt.init(parent)
            # Получение локальной (т.е. в координатной плоскости родителя, а не всего экрана) области "стрелочки" QComboBox
            arrowRect = parent.style().subControlRect(
                QtGui.QStyle.CC_ComboBox,
                opt,
                QtGui.QStyle.SC_ComboBoxArrow,
                parent
            )
            # Преобразование области из локальных координат виджета в глобальные координаты экрана
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            # Если нажатие мыши было произведено по стрелочки QComboBox или в рамках текущего всплывающего окна
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                # Запретить единожды воспроизведение нажатия мыши, когда виджет закрывается
                # atronah: вероятно, чтобы избежать повторного открытия поп-апа
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)

    def eventFilter(self, watched, event):
        if watched == self.table:
            if event.type() == QtCore.QEvent.KeyPress:
                text = forceString(event.text())
                key = event.key()
                if key in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                    event.accept()
                    index = self.table.currentIndex()
                    self.table.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                    return True
                elif text.isalpha() or text.isdigit() or key in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]:
                    self.parentWidget().event(event)
                    return True
        return QtGui.QFrame.eventFilter(self, watched, event)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        self.getCheckBoxes()
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
            self.setValueIfOnly()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()

    def setIdList(self, idList):
        if idList:
            self.table.setIdList(idList, self._id)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.table.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.chkSex.setFocus(QtCore.Qt.OtherFocusReason)

    @classmethod
    def setActionTypeIdList(self, idList):
        self._actionTypeIdList = idList

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_table_doubleClicked(self, index):
        self._isDoubleClick = True
        if index.isValid():
            if QtCore.Qt.ItemIsEnabled & self.tableModel.flags(index):
                id = self.table.currentItemId()
                self._id = id
                self.emit(QtCore.SIGNAL('ItemSelected(int)'), id)
                self.close()

    def sizeHint(self):
        size = super(CComboBoxPopup, self).sizeHint() or self.table.sizeHint()
        size.setWidth(max(size.width(),
                          self.table.sizeHint().width(),
                          640))
        return size


class CPopupTableModel(CTableModel):
    def __init__(self, parent, type='MES'):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Код', ['code'], 25))
        self.addColumn(CTextCol(u'Наименование', ['name'], 50))
        self.addColumn(CTextCol(u'Коэффициент', ['KSGNorm'], 25))
        if type == 'MES':
            self.setTable('mes.MES')
        elif type == 'CSG':
            self.setTable(u'''
            SELECT
                mes.SPR69.KSG as code,
                mes.MES.name as name,
                mes.SPR69.KSGKoeff as KSGNorm,
                mes.SPR69.id as id
            FROM
                mes.SPR69
                INNER JOIN mes.MES ON mes.SPR69.KSG = mes.MES.code
                    AND mes.MES.begDate <= mes.SPR69.endDate
                    AND mes.MES.endDate >= mes.SPR69.begDate
            ''')
        self.date = QtCore.QDate.currentDate()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
