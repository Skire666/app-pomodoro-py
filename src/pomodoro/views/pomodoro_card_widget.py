"""Compact card widget for one row of the pomodoro list (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from pomodoro.models.pomodoro_row_state import PomodoroRowState
from pomodoro.shared import i18n_fra


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
        """Lay out the card's two rows: name/duration, then quick actions."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.addLayout(self._build_header_row(row))
        layout.addLayout(self._build_actions_row())

    def _build_header_row(self, row: PomodoroRowState) -> QHBoxLayout:
        """Build row 1: the name (left, takes the remaining width) and the duration (right)."""
        header_layout = QHBoxLayout()

        name_label = QLabel(row.name)
        name_label.setObjectName("name_label")
        header_layout.addWidget(name_label, 1)

        duration_label = QLabel(format_duration(row.duration_seconds))
        duration_label.setObjectName("duration_label")
        duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(duration_label)

        return header_layout

    def _build_actions_row(self) -> QHBoxLayout:
        """Build row 2: the quick-action buttons (spec §2.1)."""
        actions_layout = QHBoxLayout()
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
        return actions_layout


# EOF
