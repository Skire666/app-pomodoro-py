"""Compact card widget for one row of the pomodoro list (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Final

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pomodoro.models.pomodoro_row_state import PomodoroRowState
from pomodoro.shared import i18n_fra

ROW_HEIGHT_PX: Final[int] = 40


def format_duration(duration_seconds: int) -> str:
    """Format a duration in seconds as HH:MM:SS."""
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class PomodoroCardWidget(QFrame):
    """One compact card in the pomodoro list: name/duration, then quick actions (spec §2.1).

    A plain click on the card is not wired to anything: only its own
    Play/Edit/Dupliquer/Supprimer actions change what the main area shows.
    """

    start_clicked = Signal(str)
    edit_clicked = Signal(str)
    duplicate_clicked = Signal(str)
    delete_clicked = Signal(str)

    def __init__(self, row: PomodoroRowState, parent: QWidget | None = None) -> None:
        """Build the card for `row` and wire its internal widgets."""
        super().__init__(parent)
        self.setObjectName("pomodoro_card_widget")
        self._id_pomodoro = row.id_pomodoro
        self._build_ui(row)

    def _build_ui(self, row: PomodoroRowState) -> None:
        """Lay out the card's two rows: name/duration, then quick actions.

        Each row is a fixed 12px tall, so the card never stretches to fill
        the list's available height (AGENTS.md spec change: fixed-height rows).
        """
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        layout.addWidget(self._build_header_row(row))
        layout.addWidget(self._build_actions_row())
        self.setFixedHeight(2 * ROW_HEIGHT_PX)

    def _build_header_row(self, row: PomodoroRowState) -> QWidget:
        """Build row 1: the name (left, takes the remaining width) and the duration (right)."""
        header_widget = QWidget()
        header_widget.setFixedHeight(ROW_HEIGHT_PX)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(4, 4, 4, 4)

        name_label = QLabel(row.name)
        name_label.setObjectName("name_label")
        header_layout.addWidget(name_label, 1)

        duration_label = QLabel(format_duration(row.duration_seconds))
        duration_label.setObjectName("duration_label")
        duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(duration_label)

        return header_widget

    def _build_actions_row(self) -> QWidget:
        """Build row 2: the quick-action buttons (spec §2.1)."""
        actions_widget = QWidget()
        actions_widget.setFixedHeight(ROW_HEIGHT_PX)
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        actions: tuple[tuple[str, str, SignalInstance], ...] = (
            ("start_button", i18n_fra.LIST_ACTION_START, self.start_clicked),
            ("edit_button", i18n_fra.LIST_ACTION_EDIT, self.edit_clicked),
            ("duplicate_button", i18n_fra.LIST_ACTION_DUPLICATE, self.duplicate_clicked),
            ("delete_button", i18n_fra.LIST_ACTION_DELETE, self.delete_clicked),
        )
        for object_name, label, signal in actions:
            button = QPushButton(label)
            button.setObjectName(object_name)
            button.clicked.connect(lambda _checked=False, s=signal: s.emit(self._id_pomodoro))
            actions_layout.addWidget(button)

        actions_layout.addStretch(1)
        return actions_widget


# EOF
