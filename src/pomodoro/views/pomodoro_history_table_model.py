"""Read-only display adapter for the pomodoro history table (spec §2.6)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Final

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QPersistentModelIndex, Qt

from pomodoro.models.pomodoro_history_row_state import PomodoroHistoryRowState
from pomodoro.shared import i18n_fra
from pomodoro.shared.enums.pomodoro_history_status_enum import PomodoroHistoryStatusEnum
from pomodoro.views.pomodoro_card_widget import format_duration

_STATUS_LABELS: Final[dict[PomodoroHistoryStatusEnum, str]] = {
    PomodoroHistoryStatusEnum.E_COMPLETED: i18n_fra.HISTORY_STATUS_COMPLETED,
    PomodoroHistoryStatusEnum.E_INTERRUPTED: i18n_fra.HISTORY_STATUS_INTERRUPTED,
}

_COLUMN_NAME: Final[int] = 0
_COLUMN_DATE: Final[int] = 1
_COLUMN_PLANNED: Final[int] = 2
_COLUMN_STATUS: Final[int] = 3
_HEADERS: Final[tuple[str, ...]] = (
    i18n_fra.HISTORY_COLUMN_NAME,
    i18n_fra.HISTORY_COLUMN_DATE,
    i18n_fra.HISTORY_COLUMN_PLANNED_DURATION,
    i18n_fra.HISTORY_COLUMN_STATUS,
)


class PomodoroHistoryTableModel(QAbstractTableModel):
    """Read-only display of pomodoro session history rows (AGENTS.md §16.5)."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the model with an empty row set."""
        super().__init__(parent)
        self._rows: tuple[PomodoroHistoryRowState, ...] = ()

    def set_rows(self, rows: tuple[PomodoroHistoryRowState, ...]) -> None:
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
    def _cell_text(row: PomodoroHistoryRowState, column: int) -> str | None:
        """Format the text for one cell of `row`."""
        if column == _COLUMN_NAME:
            name = row.name
            return f"{name} {i18n_fra.HISTORY_DELETED_BADGE}" if row.is_source_deleted else name
        if column == _COLUMN_DATE:
            return row.executed_at.strftime("%d/%m %H:%M")
        if column == _COLUMN_PLANNED:
            return format_duration(row.planned_duration_seconds)
        if column == _COLUMN_STATUS:
            return _STATUS_LABELS.get(row.status, "")
        return None


# EOF
