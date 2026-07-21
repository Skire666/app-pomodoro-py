"""Read-only display adapter for the TODO history table (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Final

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt

from pomodoro.models.todo_history_row_state import TodoHistoryRowState
from pomodoro.shared import i18n_fra
from pomodoro.views.todo_table_model import STATE_LABELS

_COLUMN_LABEL: Final[int] = 0
_COLUMN_POMODORO: Final[int] = 1
_COLUMN_TRANSITION: Final[int] = 2
_COLUMN_DATE: Final[int] = 3
_HEADERS: Final[tuple[str, ...]] = (
    i18n_fra.HISTORY_COLUMN_LABEL,
    i18n_fra.HISTORY_COLUMN_POMODORO,
    i18n_fra.HISTORY_COLUMN_TRANSITION,
    i18n_fra.HISTORY_COLUMN_DATE,
)


class TodoHistoryTableModel(QAbstractTableModel):
    """Read-only display of TODO state-change history rows (AGENTS.md §16.5)."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the model with an empty row set."""
        super().__init__(parent)
        self._rows: tuple[TodoHistoryRowState, ...] = ()

    def set_rows(self, rows: tuple[TodoHistoryRowState, ...]) -> None:
        """Replace every row and reset the model."""
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Return the number of history rows currently displayed."""
        index = parent if parent is not None else QModelIndex()
        return 0 if index.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Return the number of columns."""
        index = parent if parent is not None else QModelIndex()
        return 0 if index.isValid() else len(_HEADERS)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object:
        """Return the column header text."""
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        return _HEADERS[section] if 0 <= section < len(_HEADERS) else None

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        """Return the display value for `index`."""
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if not (0 <= index.row() < len(self._rows)):
            return None
        return self._cell_text(self._rows[index.row()], index.column())

    @staticmethod
    def _cell_text(row: TodoHistoryRowState, column: int) -> str | None:
        """Format the text for one cell of `row`."""
        if column == _COLUMN_LABEL:
            return row.label
        if column == _COLUMN_POMODORO:
            return row.pomodoro_name
        if column == _COLUMN_TRANSITION:
            old_label = STATE_LABELS.get(row.old_state, "")
            new_label = STATE_LABELS.get(row.new_state, "")
            return f"{old_label} → {new_label}"
        if column == _COLUMN_DATE:
            return row.changed_at.strftime("%d/%m %H:%M")
        return None


# EOF
