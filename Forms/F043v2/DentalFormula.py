# coding=utf-8

from PyQt4 import QtCore, QtGui
import math
from PyQt4 import QtSql

from library.Utils import forceString, forceRef, forceBool, forceDate
from library.crbcombobox import CRBComboBox


TOOTH_SIZE = 70
TOOTH_LIST = (18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28,
              38, 37, 36, 35, 34, 33, 32, 31, 41, 42, 43, 44, 45, 46, 47, 48)
TEETH_ROWS = (2, 5)
NUMBER_ROWS = (3, 4)
MOBILITY_ROWS = (1, 6)
STATUS_ROWS = (0, 7)


class ToothSectionStateModel(QtCore.QAbstractTableModel):
    def __init__(self, items, parent=None):
        super(ToothSectionStateModel, self).__init__(parent)
        self.items = items

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            row, col = index.row(), index.column()
            if col == 0:
                return QtCore.QVariant(self.items[row].code)
            elif col == 1:
                return QtCore.QVariant(self.items[row].name)
        return QtCore.QVariant()

    def headerData(self, idx, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if idx == 0:
                return QtCore.QVariant(u'Код')
            elif idx == 1:
                return QtCore.QVariant(u'Наименование')

    def index(self, row, col, parent=None, *args, **kwargs):
        return self.createIndex(row, col, self.items[row])


class StatesTableView(QtGui.QTableView):
    changed = QtCore.pyqtSignal(set, set, bool)  # selected id list, deselected id list, is whole tooth

    def __init__(self, parent=None):
        super(StatesTableView, self).__init__(parent)
        self.horizontalHeader().resizeSection(0, 50)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.setDragEnabled(False)

        self.ignore_selection = False

    def mouseMoveEvent(self, evt):
        # hack: ignore drag selection
        pass

    def selectionChanged(self, selected, deselected):
        super(StatesTableView, self).selectionChanged(selected, deselected)
        if self.ignore_selection:
            return

        whole_tooth = False
        # limit selection to two rows
        if len(self.selectedIndexes()) > 4:  # 2 rows x 2 cols
            self.selectionModel().select(self.selectedIndexes()[-1], QtGui.QItemSelectionModel.Deselect)
        elif len(selected.indexes()):
            # if selected state applies to whole tooth, make it the only selected one
            if len(selected.indexes()) and selected.indexes()[-1].internalPointer().whole:
                self.ignore_selection = True
                row = self.selectedIndexes()[-1].row()
                self.clearSelection()
                self.selectRow(row)
                self.ignore_selection = False
                whole_tooth = True
            # if whole tooth state is already selected, disallow selection change (unless it isn't state deselection)
            elif len(self.selectedIndexes()) and self.selectedIndexes()[0].internalPointer().whole:
                self.ignore_selection = True
                row = self.selectedIndexes()[0].row()
                self.clearSelection()
                self.selectRow(row)
                self.ignore_selection = False
                return
        selected_ids = set(index.internalPointer().item_id for index in selected.indexes())
        deselected_ids = set(index.internalPointer().item_id for index in deselected.indexes())
        self.changed.emit(selected_ids, deselected_ids, whole_tooth)

    def set_selection(self, ids):
        self.ignore_selection = True
        self.clearSelection()
        for row, val in filter(lambda x: x[1].item_id in ids, enumerate(self.model().items)):
            self.selectRow(row)
        self.ignore_selection = False


class ToothSections:
    def __init__(self):
        self.U = set()
        self.D = set()
        self.R = set()
        self.L = set()
        self.CL = set()
        self.CR = set()
        self.FULL = set()

    def set_full(self, value):
        ToothSections.__init__(self)
        self.FULL = set([value])

    @classmethod
    def from_db(cls, tooth_id, states):
        db = QtGui.qApp.db

        s = cls()
        ids = dict()
        for rec in db.getRecordList('DentalFormulaTeethSections', '*', 'tooth_id=%d' % tooth_id):
            ids.setdefault(forceString(rec.value('section')), set()).add(states[forceRef(rec.value('state_id'))])
        if 'FULL' in ids:
            s.FULL = ids['FULL']
        else:
            for k, v in ids.iteritems():
                setattr(s, k, v)
        return s

    @staticmethod
    def get_record(tooth_id, section, state_id):
        rec = QtSql.QSqlRecord()
        rec.append(QtSql.QSqlField('id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('tooth_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('section', QtCore.QVariant.String))
        rec.append(QtSql.QSqlField('state_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('deleted', QtCore.QVariant.Bool))
        rec.setValue('tooth_id', tooth_id)
        rec.setValue('section', section)
        rec.setValue('state_id', state_id)
        return rec

    def save_states(self, tooth_id, section, states):
        db = QtGui.qApp.db

        for state in states:
            db.insertRecord('DentalFormulaTeethSections', self.get_record(tooth_id, section, state.item_id))

    def has_values(self):
        return self.U or self.D or self.L or self.R or self.CL or self.CR or self.FULL

    def save(self, tooth_id):
        if self.FULL:
            self.save_states(tooth_id, 'FULL', self.FULL)
            return
        self.save_states(tooth_id, 'U', self.U)
        self.save_states(tooth_id, 'D', self.D)
        self.save_states(tooth_id, 'L', self.L)
        self.save_states(tooth_id, 'R', self.R)
        self.save_states(tooth_id, 'CL', self.CL)
        self.save_states(tooth_id, 'CR', self.CR)


class ToothStatus:
    def __init__(self, item_id, code, name, color):
        self.item_id = item_id
        self.code = code
        self.name = name
        self.color = color

    @classmethod
    def from_record(cls, rec):
        return cls(
            forceRef(rec.value('id')),
            forceString(rec.value('code')),
            forceString(rec.value('name')),
            forceString(rec.value('color'))
        )


class ToothSectionState:
    def __init__(self, item_id, code, flat_code, name, whole):
        self.item_id = item_id
        self.code = code
        self.flat_code = flat_code
        self.name = name
        self.whole = whole

    @classmethod
    def from_record(cls, rec):
        return cls(
            forceRef(rec.value('id')),
            forceString(rec.value('code')),
            forceString(rec.value('flatCode')),
            forceString(rec.value('name')),
            forceBool(rec.value('wholeTooth'))
        )


class Tooth:
    def __init__(self, number):
        self.is_deciduous = False
        self.number = number
        self.status = self.mobility = None
        self.sections = ToothSections()
        self.selection = set()
        self.mobility = 0

    @classmethod
    def from_record(cls, rec, states, states_only=False):
        t = cls(forceRef(rec.value('number')))  # type: Tooth
        t.is_deciduous = forceBool(rec.value('is_deciduous'))
        t.sections = ToothSections.from_db(forceRef(rec.value('id')), states)
        if not states_only:
            t.status = forceRef(rec.value('status_id'))
            t.mobility = forceRef(rec.value('mobility'))
        return t

    @staticmethod
    def empty_record():
        rec = QtSql.QSqlRecord()
        rec.append(QtSql.QSqlField('id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('formula_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('number', QtCore.QVariant.String))
        rec.append(QtSql.QSqlField('is_deciduous', QtCore.QVariant.Bool))
        rec.append(QtSql.QSqlField('status_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('mobility', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('deleted', QtCore.QVariant.Bool))
        return rec

    def get_number(self):
        if self.is_deciduous:
            return str(self.number + 40)
        else:
            return str(self.number)

    def is_simplified(self):
        return self.number and (self.number % 10 <= 3)

    def get_section(self, point):
        x, y = point.x() - TOOTH_SIZE / 2, point.y() - TOOTH_SIZE / 2
        r = math.sqrt(x ** 2 + y ** 2)
        phi = math.atan2(y, x) / math.pi
        # phi = 0 строго справа; против часовой стрелки - минус, по - плюс (до pi, где phi = 1)
        if r > TOOTH_SIZE / 2:
            return None

        if self.sections.FULL:
            return 'FULL'

        if not self.is_simplified():
            if r < TOOTH_SIZE / 4:
                if abs(phi) > .5:
                    return 'CL'
                else:
                    return 'CR'
        if abs(phi) <= .25:
            return 'R'
        elif abs(phi) >= .75:
            return 'L'
        elif .25 < phi < .75:
            return 'D'
        elif -.25 > phi > -.75:
            return 'U'

    def create_tooth(self, formula):
        db = QtGui.qApp.db

        rec = self.empty_record()
        rec.setValue('status_id', self.status)
        rec.setValue('mobility', self.mobility)
        rec.setValue('is_deciduous', self.is_deciduous)
        rec.setValue('number', self.number)
        rec.setValue('formula_id', formula)
        db.insertRecord('DentalFormulaTeeth', rec)
        return forceRef(rec.value('id'))

    def save(self, formula):
        if self.sections.has_values() or self.mobility or self.status or self.is_deciduous:
            tooth_id = self.create_tooth(formula)
            self.sections.save(tooth_id)


class DentalFormulaModel(QtCore.QAbstractTableModel):
    def __init__(self, view):
        super(DentalFormulaModel, self).__init__()
        self._view = view
        self.is_deciduous = False
        self.record = self.empty_record()
        self.items = dict((num, Tooth(num)) for num in TOOTH_LIST)
        self.states, self.statuses = self.load_ref_books()

    @staticmethod
    def empty_record():
        rec = QtSql.QSqlRecord()
        rec.append(QtSql.QSqlField('id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('event_id', QtCore.QVariant.ULongLong))
        rec.append(QtSql.QSqlField('is_deciduous', QtCore.QVariant.Bool))
        return rec

    def set_event_id(self, event_id):
        self.record.setValue('event_id', QtCore.QVariant(event_id))

    def load_event(self, event_id, states_only=False, copy=False):
        self.is_deciduous = False
        if not copy:
            self.record = self.empty_record()
        self.items = dict((num, Tooth(num)) for num in TOOTH_LIST)

        db = QtGui.qApp.db

        rec = db.getRecordEx('DentalFormula', '*', 'event_id=%d' % event_id)
        if rec:
            if not copy:
                self.record = rec
            self.is_deciduous = forceBool(rec.value('is_deciduous'))
            for tooth_rec in db.getRecordList('DentalFormulaTeeth', '*', 'formula_id=%d AND deleted=0' % forceRef(rec.value('id'))):
                number = forceRef(tooth_rec.value('number'))
                tooth = Tooth.from_record(tooth_rec, self.states, states_only)
                if number in self.items and states_only:
                    tooth.sections = self.items[number].sections
                    tooth.status = self.items[number].status
                self.items[number] = tooth
        elif not copy:
            self.set_event_id(event_id)
        self.reset()

    @staticmethod
    def load_ref_books():
        db = QtGui.qApp.db

        states = dict((forceRef(rec.value('id')), ToothSectionState.from_record(rec))
                      for rec in db.getRecordList('rbToothSectionState', '*', 'deleted=0'))
        statuses = dict((forceRef(rec.value('id')), ToothStatus.from_record(rec))
                        for rec in db.getRecordList('rbToothStatus', '*', 'deleted=0'))
        return states, statuses

    def rowCount(self, parent=None, *args, **kwargs):
        return 8

    def columnCount(self, parent=None, *args, **kwargs):
        return 10 if self.is_deciduous else 16

    def get_tooth(self, row, col):
        col -= 8
        if self.is_deciduous:
            col += 3
        if row <= 3:
            if col < 0:
                num = 10 + abs(col)
            else:
                num = 20 + col + 1
        else:
            if col < 0:
                num = 40 + abs(col)
            else:
                num = 30 + col + 1
        return self.items[num]

    def index(self, row, col, parent=None, *args, **kwargs):
        return self.createIndex(row, col, self.get_tooth(row, col))

    def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                if index in STATUS_ROWS:
                    return QtCore.QVariant(u'Статус')
                elif index in MOBILITY_ROWS:
                    return QtCore.QVariant(u'Подвижность')
                elif index in TEETH_ROWS:
                    return QtCore.QVariant(u'Состояние')
                elif index in NUMBER_ROWS:
                    return QtCore.QVariant(u'Номер')
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if row in STATUS_ROWS:
                status = index.internalPointer().status
                return QtCore.QVariant(u'' if not status else self.statuses[status].name)
            elif row in MOBILITY_ROWS:
                mobility = index.internalPointer().mobility
                return QtCore.QVariant(u'---' if not mobility else unicode(mobility))
            elif row in NUMBER_ROWS:
                return QtCore.QVariant(self.get_tooth(row, col).get_number())
        elif role == QtCore.Qt.TextAlignmentRole and row in NUMBER_ROWS:
            return QtCore.Qt.AlignCenter
        if row in STATUS_ROWS:
            status = index.internalPointer().status
            if status:
                status_obj = self.statuses[status]
                if status_obj.color:
                    bg = QtGui.QColor(status_obj.color)
                    if role == QtCore.Qt.BackgroundRole:
                        return QtGui.QBrush(bg)
                    elif role == QtCore.Qt.ForegroundRole:
                        # http://stackoverflow.com/a/1855903/5139327
                        a = 1 - (.299 * bg.red() + .587 * bg.green() + .114 * bg.blue()) / 255
                        return QtGui.QBrush(QtCore.Qt.black if a < .5 else QtCore.Qt.white)
        return QtCore.QVariant()

    def set_states(self, selected_ids, deselected_ids):
        for tooth in self.items.values():
            if tooth.selection:
                if 'FULL' in tooth.selection:
                    tooth.selection.remove('FULL')
                    tooth.sections.FULL = set()
                for section in tooth.selection:
                    getattr(tooth.sections, section).difference_update(set(self.states[state_id] for state_id in deselected_ids))
                    if len(getattr(tooth.sections, section).union(set(self.states[state_id] for state_id in selected_ids))) <= 2:
                        getattr(tooth.sections, section).update(set(self.states[state_id] for state_id in selected_ids))
                    # setattr(tooth.sections, section, set(self.states[state_id] for state_id in ids))
        self.dataChanged.emit(self.index(TEETH_ROWS[0], 0), self.index(TEETH_ROWS[1], self.columnCount()-1))

    def set_whole_state(self, selected_ids, deselected_ids):
        for tooth in self.items.values():
            if tooth.selection:
                tooth.sections.set_full(self.states[list(selected_ids)[0]])
                tooth.selection.add('FULL')
        self.dataChanged.emit(self.index(TEETH_ROWS[0], 0), self.index(TEETH_ROWS[1], self.columnCount()-1))

    def save(self):
        db = QtGui.qApp.db

        self.record.setValue('is_deciduous', self.is_deciduous)
        db.insertOrUpdate('DentalFormula', self.record)
        formula_id = forceRef(self.record.value('id'))
        db.markRecordsDeleted('DentalFormulaTeeth', 'formula_id=%d' % formula_id)
        for tooth in self.items.values():
            tooth.save(formula_id)

    def flags(self, idx):
        row = idx.row()
        flags = super(DentalFormulaModel, self).flags(idx)
        if row in MOBILITY_ROWS + STATUS_ROWS and self._view._editable:
            return flags | QtCore.Qt.ItemIsEditable
        return flags


class ToothSchemaDelegate(QtGui.QStyledItemDelegate):
    @staticmethod
    def get_brush(section, index):
        if section in index.internalPointer().selection or 'FULL' in index.internalPointer().selection:
            return QtGui.QBrush(QtCore.Qt.cyan)
        else:
            return QtGui.QBrush(QtCore.Qt.white)

    @staticmethod
    def get_font(size_multiplier=1):
        f = QtGui.QFont()
        f.setStyleHint(QtGui.QFont.Monospace)
        f.setPixelSize(10 * size_multiplier)
        return f

    @staticmethod
    def get_large_font(size_multiplier=1):
        f = ToothSchemaDelegate.get_font()
        f.setPixelSize(20 * size_multiplier)
        return f

    def paint(self, painter, option, index):
        """
        :type painter: QtGui.QPainter
        """
        sections = index.internalPointer().sections
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.setFont(self.get_font())
        r = option.rect
        x, y, w, h = r.x(), r.y(), r.width(), r.height()

        if sections.FULL:
            painter.setFont(self.get_large_font())
            painter.setBrush(self.get_brush('FULL', index))
            painter.drawEllipse(r)
            painter.drawText(r, QtCore.Qt.AlignCenter, '\n'.join((state.code for state in sections.FULL)))
            return

        painter.setBrush(self.get_brush('U', index))
        painter.drawPie(r, 45 * 16, 90 * 16)   # U
        painter.setBrush(self.get_brush('L', index))
        painter.drawPie(r, 135 * 16, 90 * 16)  # L
        painter.setBrush(self.get_brush('D', index))
        painter.drawPie(r, 225 * 16, 90 * 16)  # D
        painter.setBrush(self.get_brush('R', index))
        painter.drawPie(r, 315 * 16, 90 * 16)  # R

        if not index.internalPointer().is_simplified():
            r = QtCore.QRect(x + w/4, y + h/4, w/2, h/2)
            painter.setBrush(self.get_brush('CL', index))
            painter.drawPie(r, 90 * 16, 180 * 16)   # CL
            painter.setBrush(self.get_brush('CR', index))
            painter.drawPie(r, 270 * 16, 180 * 16)  # CR

            painter.drawText(
                QtCore.QRect(x, y, w/4, h),
                QtCore.Qt.AlignCenter,
                '\n'.join((state.code for state in sections.L))
            )
            painter.drawText(
                QtCore.QRect(x, y, w, h/4),
                QtCore.Qt.AlignCenter,
                ' '.join((state.code for state in sections.U))
            )
            painter.drawText(
                QtCore.QRect(x+w*3/4, y, w/4, h),
                QtCore.Qt.AlignCenter,
                '\n'.join((state.code for state in sections.R))
            )
            painter.drawText(
                QtCore.QRect(x, y+h*3/4, w, h/4),
                QtCore.Qt.AlignCenter,
                ' '.join((state.code for state in sections.D))
            )
            painter.drawText(
                QtCore.QRect(x+w/4, y, w/4, h),
                QtCore.Qt.AlignCenter,
                '\n'.join((state.code for state in sections.CL))
            )
            painter.drawText(
                QtCore.QRect(x+w*2/4, y, w/4, h),
                QtCore.Qt.AlignCenter,
                '\n'.join((state.code for state in sections.CR))
            )
        else:
            painter.drawText(
                QtCore.QRect(x, y, w/2, h),
                QtCore.Qt.AlignCenter,
                '\n'.join((state.code for state in sections.L))
            )
            painter.drawText(
                QtCore.QRect(x, y, w, h/2),
                QtCore.Qt.AlignCenter,
                ' '.join((state.code for state in sections.U))
            )
            painter.drawText(
                QtCore.QRect(x+w/2, y, w/2, h),
                QtCore.Qt.AlignCenter,
                '\n'.join((state.code for state in sections.R))
            )
            painter.drawText(
                QtCore.QRect(x, y+h/2, w, h/2),
                QtCore.Qt.AlignCenter,
                ' '.join((state.code for state in sections.D))
            )


class MobilityDelegate(QtGui.QStyledItemDelegate):
    @staticmethod
    def get_tooth(index):
        return index.internalPointer()

    def createEditor(self, parent, option, index):
        cmb = QtGui.QComboBox(parent)
        cmb.addItems((u'0', u'1', u'2', u'3'))
        return cmb

    def setEditorData(self, editor, index):
        mobility = self.get_tooth(index).mobility
        editor.setCurrentIndex(mobility if mobility else 0)

    def setModelData(self, editor, model, index):
        self.get_tooth(index).mobility = editor.currentIndex()


class StatusDelegate(QtGui.QStyledItemDelegate):
    @staticmethod
    def get_tooth(index):
        return index.internalPointer()

    def createEditor(self, parent, option, index):
        cmb = CRBComboBox(parent)
        cmb.setTable('rbToothStatus')
        return cmb

    def setEditorData(self, editor, index):
        editor.setValue(self.get_tooth(index).status)

    def setModelData(self, editor, model, index):
        self.get_tooth(index).status = editor.value()


class DentalFormulaView(QtGui.QTableView):
    selection_changed = QtCore.pyqtSignal(set)

    def __init__(self, parent=None):
        super(DentalFormulaView, self).__init__(parent)
        self._model = DentalFormulaModel(self)
        self.setModel(self._model)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._editable = True
        self._tooth_delegate = ToothSchemaDelegate()
        self._mobility_delegate = MobilityDelegate()
        self._status_delegate = StatusDelegate()
        for row in TEETH_ROWS:
            self.setItemDelegateForRow(row, self._tooth_delegate)
        for row in MOBILITY_ROWS:
            self.setItemDelegateForRow(row, self._mobility_delegate)
        for row in STATUS_ROWS:
            self.setItemDelegateForRow(row, self._status_delegate)

        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setDefaultSectionSize(TOOTH_SIZE)
        self.verticalHeader().setHighlightSections(False)
        for row in TEETH_ROWS:
            self.verticalHeader().resizeSection(row, TOOTH_SIZE)
        self.setSelectionMode(QtGui.QTableView.NoSelection)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

        self.clicked.connect(self.table_clicked)
        self.customContextMenuRequested.connect(self.context_menu)

        self.ctx_index = None
        self._tooth_type_act = QtGui.QAction(u'Изменить тип зуба', self)
        self._tooth_type_act.triggered.connect(self.change_tooth_type)
        self._schema_type_act = QtGui.QAction(u'Изменить тип схемы', self)
        self._schema_type_act.triggered.connect(self.change_schema_type)

    def set_editable(self, val):
        self._editable = val

    def change_tooth_type(self):
        tooth = self.ctx_index.internalPointer()
        tooth.is_deciduous = not tooth.is_deciduous
        self._model.reset()

    def change_schema_type(self):
        self._model.is_deciduous = not self._model.is_deciduous
        for tooth in self._model.items.values():
            tooth.is_deciduous = self._model.is_deciduous
        self._model.reset()

    def context_menu(self, point):
        if not self._editable:
            return
        self.ctx_index = index = self.indexAt(point)
        menu = QtGui.QMenu(self)
        menu.addAction(self._schema_type_act)
        if index.internalPointer().number % 10 <= 5:
            menu.addAction(self._tooth_type_act)
        menu.popup(self.viewport().mapToGlobal(point))

    def load_event(self, event_id, states_only=False, copy=False):
        self._model.load_event(event_id, states_only, copy)

    def is_deciduous(self):
        return self._model.is_deciduous

    def table_clicked(self, index):
        if not self._editable:
            return

        ctrl = QtGui.qApp.keyboardModifiers() & QtCore.Qt.CTRL
        if not ctrl:
            for tooth in self._model.items.values():
                tooth.selection.clear()
            self.selection_changed.emit(set([None]))

        if index.isValid():
            if index.row() in TEETH_ROWS:
                cursor = QtGui.QCursor().pos()
                p = cursor - self.mapToGlobal(self.visualRect(index).topLeft()) - self.verticalHeader().rect().topRight()
                section = index.internalPointer().get_section(p)
                if section:
                    if ctrl:
                        if section in index.internalPointer().selection:
                            index.internalPointer().selection.remove(section)
                        else:
                            index.internalPointer().selection.add(section)
                        self.selection_changed.emit(set())
                    else:
                        index.internalPointer().selection.add(section)
                        self.selection_changed.emit(set(s.item_id for s in getattr(index.internalPointer().sections, section)))
            elif index.row() in NUMBER_ROWS:
                tooth = self.model().get_tooth(index.row(), index.column())
                if tooth.sections.FULL:
                    selection = set(['FULL'])
                else:
                    selection = set(['U', 'D', 'L', 'R'])
                    if not tooth.is_simplified():
                        selection.update(set(['CL', 'CR']))
                tooth.selection = selection
                self.selection_changed.emit(set())

        self.viewport().update()

    def save(self):
        self._model.save()


class HistoryListModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(HistoryListModel, self).__init__()
        self._items = []

    def loadItems(self, client_id, event_id):
        for record in QtGui.qApp.db.getRecordList(
                stmt='SELECT e.id as id, e.createDatetime as date '
                     'FROM DentalFormula df '
                     'INNER JOIN Event e ON df.event_id = e.id '
                     '                      AND e.client_id = %d '
                     '                      AND e.deleted = 0'
                     '                      AND e.id <> %d '
                     'ORDER BY e.createDatetime DESC' % (client_id, event_id or -1)):
            self._items.append((forceRef(record.value('id')), forceDate(record.value('date'))))
        self.reset()

    def index(self, row, column=0, parent=None, *args, **kwargs):
        if 0 <= row <= self.rowCount():
            return self.createIndex(row, column, self._items[row])
        return QtCore.QModelIndex()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._items)

    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            return QtCore.QVariant(self._items[row][1])
        return QtCore.QVariant()

