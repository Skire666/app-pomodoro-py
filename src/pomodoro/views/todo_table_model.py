"""Display adapter wrapping `TodoRowState` rows for a `QTableView` (spec §2.5)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Final

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt, Signal

from pomodoro.models.todo_row_state import TodoRowState
from pomodoro.shared import i18n_fra
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum

STATE_LABELS: Final[dict[TodoStateEnum, str]] = {
    TodoStateEnum.E_TODO: i18n_fra.TODO_STATE_TODO,
    TodoStateEnum.E_IN_PROGRESS: i18n_fra.TODO_STATE_IN_PROGRESS,
    TodoStateEnum.E_DONE: i18n_fra.TODO_STATE_DONE,
    TodoStateEnum.E_CANCELLED: i18n_fra.TODO_STATE_CANCELLED,
}

COLUMN_LABEL: Final[int] = 0
COLUMN_STATE: Final[int] = 1
_COLUMN_COUNT: Final[int] = 2


class TodoTableModel(QAbstractTableModel):
    """Read-only display of TODO rows, with inline editing of the label column only.

    A pure display adapter (AGENTS.md §16.5): it holds no business logic and
    merely emits `label_edited` for the Presenter to validate and persist.
    """

    label_edited = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the model with an empty row set."""
        super().__init__(parent)
        self._rows: tuple[TodoRowState, ...] = ()

    def set_rows(self, rows: tuple[TodoRowState, ...]) -> None:
        """Replace every row and reset the model (spec §2.5)."""
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def row_at(self, row_index: int) -> TodoRowState | None:
        """Return the row state at `row_index`, or None if out of range."""
        if 0 <= row_index < len(self._rows):
            return self._rows[row_index]
        return None

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Return the number of TODO rows currently displayed."""
        index = parent if parent is not None else QModelIndex()
        return 0 if index.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Return the number of columns (label, state)."""
        index = parent if parent is not None else QModelIndex()
        return 0 if index.isValid() else _COLUMN_COUNT

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object:
        """Return the column header text."""
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        if section == COLUMN_LABEL:
            return i18n_fra.TODO_COLUMN_LABEL_HEADER
        return i18n_fra.TODO_COLUMN_STATE_HEADER

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        """Return the display/edit value for `index`."""
        if role not in {Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole}:
            return None
        row = self.row_at(index.row())
        if row is None:
            return None
        if index.column() == COLUMN_LABEL:
            return row.label
        if index.column() == COLUMN_STATE:
            return STATE_LABELS.get(row.state, "")
        return None

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        """Return the item flags: the label column is editable, the state column is not."""
        base_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == COLUMN_LABEL:
            return base_flags | Qt.ItemFlag.ItemIsEditable
        return base_flags

    def setData(
        self, index: QModelIndex | QPersistentModelIndex, value: object, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        """Emit `label_edited` for an inline label edit; reject anything else."""
        if role != Qt.ItemDataRole.EditRole or index.column() != COLUMN_LABEL:
            return False
        row = self.row_at(index.row())
        if row is None or not isinstance(value, str):
            return False
        self.label_edited.emit(row.id_todo_item, value)
        return True


# EOF
