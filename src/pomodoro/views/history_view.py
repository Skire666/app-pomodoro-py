"""Read-only history screen: pomodoro sessions and TODO changes (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from PySide6.QtWidgets import QMessageBox, QTableView, QTabWidget, QVBoxLayout, QWidget

from pomodoro.models.pomodoro_history_row_state import PomodoroHistoryRowState
from pomodoro.models.todo_history_row_state import TodoHistoryRowState
from pomodoro.shared import i18n_fra
from pomodoro.shared.validation_result import ValidationResult
from pomodoro.views.pomodoro_history_table_model import PomodoroHistoryTableModel
from pomodoro.views.todo_history_table_model import TodoHistoryTableModel


class HistoryView(QWidget):
    """Two read-only tables: pomodoro session history and TODO change history (spec §2.6)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the two history tables inside their own tabs."""
        super().__init__(parent)
        self.setObjectName("history_view")
        self._build_ui()

    def _build_ui(self) -> None:
        """Lay out the tab widget hosting both history tables."""
        layout = QVBoxLayout(self)
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tab_widget")

        self._pomodoro_model = PomodoroHistoryTableModel(self)
        self._pomodoro_table_view = QTableView()
        self._pomodoro_table_view.setObjectName("pomodoro_history_table_view")
        self._pomodoro_table_view.setModel(self._pomodoro_model)
        self._pomodoro_table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._pomodoro_table_view.horizontalHeader().setStretchLastSection(True)
        tab_widget.addTab(self._pomodoro_table_view, i18n_fra.HISTORY_POMODORO_TAB)

        self._todo_model = TodoHistoryTableModel(self)
        self._todo_table_view = QTableView()
        self._todo_table_view.setObjectName("todo_history_table_view")
        self._todo_table_view.setModel(self._todo_model)
        self._todo_table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._todo_table_view.horizontalHeader().setStretchLastSection(True)
        tab_widget.addTab(self._todo_table_view, i18n_fra.HISTORY_TODO_TAB)

        layout.addWidget(tab_widget)

    @property
    def is_busy(self) -> bool:
        """This screen performs no long-running work of its own."""
        return False

    @property
    def is_loading(self) -> bool:
        """This screen has no separate loading phase after construction."""
        return False

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole screen."""
        self.setEnabled(enabled)

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed refresh to the user."""
        if rs.error_code is not None:
            QMessageBox.warning(self, i18n_fra.DIALOG_ERROR_TITLE, rs.error_code.message)

    def clear(self) -> None:
        """Empty both in-memory tables."""
        self._pomodoro_model.set_rows(())
        self._todo_model.set_rows(())

    def notify_pomodoro_history_refresh(self, context: tuple[PomodoroHistoryRowState, ...]) -> None:
        """Replace the pomodoro history table's rows with `context`."""
        self._pomodoro_model.set_rows(context)

    def notify_todo_history_refresh(self, context: tuple[TodoHistoryRowState, ...]) -> None:
        """Replace the TODO history table's rows with `context`."""
        self._todo_model.set_rows(context)


# EOF
