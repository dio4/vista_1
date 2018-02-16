# coding=utf-8
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui

from Forms.F043v2.DentalFormula import ToothSectionStateModel, HistoryListModel
from Forms.F043v2.Ui_DentalFormula import Ui_DentalFormula
from library.DialogBase import CDialogBase
from library.Utils import forceRef


class DentalFormulaWidget(Ui_DentalFormula, QtGui.QWidget):
    def __init__(self, parent=None):
        super(DentalFormulaWidget, self).__init__(parent)
        self.setupUi(self)
        self.tblFormula.selection_changed.connect(self.selection_changed)
        self.tblStates.setModel(ToothSectionStateModel(self.tblFormula.model().states.values()))
        self.tblStates.changed.connect(self.state_changed)
        self.btnResetStates.clicked.connect(self.reset_state)
        self.wdgHistory.setVisible(False)
        self.tblFormulaHistoryView.set_editable(False)
        self.tblFormulaHistoryView.setEnabled(False)
        self.btnHistoryToggle.toggled.connect(self.toggle_history)
        self.lstHistory.setModel(HistoryListModel())
        self.lstHistory.clicked.connect(self.load_history)

        self.lstHistory.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lstHistory.customContextMenuRequested.connect(self.history_context_menu)
        self.ctx_index = None
        self._copy_full = QtGui.QAction(u'Копировать полностью', self)
        self._copy_full.triggered.connect(self.copy_full)
        self._copy_states = QtGui.QAction(u'Копировать только состояния', self)
        self._copy_states.triggered.connect(self.copy_states)

    def toggle_history(self, val):
        self.btnHistoryToggle.setText(u'Показать историю' if not val else u'Скрыть историю')

    def load_history(self, index):
        current = index.internalPointer()
        self.tblFormulaHistoryView.load_event(current[0])
        self.tblFormulaHistoryView.setEnabled(True)

    def history_context_menu(self, point):
        self.ctx_index = self.lstHistory.indexAt(point)
        menu = QtGui.QMenu(self.lstHistory)
        menu.addAction(self._copy_full)
        menu.addAction(self._copy_states)
        menu.popup(self.lstHistory.viewport().mapToGlobal(point))

    def copy_full(self):
        self.tblFormula.load_event(self.ctx_index.internalPointer()[0], copy=True)

    def copy_states(self):
        self.tblFormula.load_event(self.ctx_index.internalPointer()[0], states_only=True, copy=True)

    def load_last_formula(self):
        pass

    def reset_state(self):
        self.tblStates.clearSelection()
        self.tblFormula.model().set_states(set(), self.tblFormula.model().states.keys())

    def state_changed(self, selected_ids, deselected_ids, whole):
        if not whole:
            self.tblFormula.model().set_states(selected_ids, deselected_ids)
        else:
            self.tblFormula.model().set_whole_state(selected_ids, deselected_ids)

    def selection_changed(self, states):
        if None in states:
            self.tblStates.clearSelection()
            self.tblStates.setEnabled(False)
        else:
            self.tblStates.setEnabled(True)
            self.tblStates.set_selection(states)


class DentalFormulaDialog(CDialogBase):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        self.w = DentalFormulaWidget(self)
        l.addWidget(self.w)
        self.setWindowTitle(u'Зубная формула')
        self.setObjectName('dlgDentalFormula')

    def set_event_id(self, event_id):
        self.w.tblFormula.load_event(event_id)

    def save(self, event_id):
        self.w.tblFormula.model().set_event_id(event_id)
        self.w.tblFormula.model().save()

    def show(self):
        self.loadDialogPreferences()
        CDialogBase.show(self)

    def hide(self):
        self.saveDialogPreferences()
        CDialogBase.hide(self)

    def formula_printer(self):
        from DentalFormulaPrint import formula_printer
        return formula_printer(self.w.tblFormula.model())

    def set_client(self, client_id):
        self.w.lstHistory.model().loadItems(client_id, forceRef(self.w.tblFormula.model().record.value('event_id')))
        if self.w.lstHistory.model().rowCount():
            self.w.tblFormula.load_event(self.w.lstHistory.model().index(0).internalPointer()[0],
                                         copy=True, states_only=True)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    v = DentalFormulaWidget()
    v.show()
    v.resize(1500, 400)
    sys.exit(app.exec_())
