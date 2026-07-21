"""Read-only pomodoro detail screen (spec §2.2)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from pomodoro.models.pomodoro_detail_view_state import PomodoroDetailViewState
from pomodoro.shared import i18n_fra
from pomodoro.shared.validation_result import ValidationResult
from pomodoro.views.pomodoro_card_widget import format_duration


class PomodoroDetailView(QWidget):
    """Read-only pomodoro summary: 'Général' frame stacked above 'TODO' (spec §2.2)."""

    def __init__(self, todo_list_view: QWidget, parent: QWidget | None = None) -> None:
        """Build the detail screen's widgets, embedding `todo_list_view` in its TODO frame."""
        super().__init__(parent)
        self.setObjectName("pomodoro_detail_view")
        self._todo_list_view = todo_list_view
        self._build_ui()

    def _build_ui(self) -> None:
        """Lay out the header, the stacked Général/TODO frames, and 'Démarrer' button."""
        layout = QVBoxLayout(self)
        layout.addLayout(self._build_header())
        layout.addWidget(self._build_general_frame())
        layout.addWidget(self._build_todo_frame(), 1)

        self._start_button = QPushButton(i18n_fra.LIST_ACTION_START)
        self._start_button.setObjectName("start_button")
        layout.addWidget(self._start_button)

    def _build_header(self) -> QHBoxLayout:
        """Build the name/edit header row."""
        header_layout = QHBoxLayout()
        self._name_label = QLabel()
        self._name_label.setObjectName("name_label")
        header_layout.addWidget(self._name_label, 1)

        self._edit_button = QPushButton(i18n_fra.LIST_ACTION_EDIT)
        self._edit_button.setObjectName("edit_button")
        header_layout.addWidget(self._edit_button)
        return header_layout

    def _build_general_frame(self) -> QWidget:
        """Build the top frame: the read-only 'Général' summary (spec change: no more tabs)."""
        general_frame = QFrame()
        general_frame.setObjectName("general_frame")
        general_frame.setFrameShape(QFrame.Shape.StyledPanel)
        general_layout = QVBoxLayout(general_frame)

        title_label = QLabel(i18n_fra.DETAIL_TAB_GENERAL)
        title_label.setObjectName("general_title_label")
        general_layout.addWidget(title_label)

        self._duration_label = QLabel()
        self._duration_label.setObjectName("duration_label")
        general_layout.addWidget(self._duration_label)

        self._sound_label = QLabel()
        self._sound_label.setObjectName("sound_label")
        general_layout.addWidget(self._sound_label)

        return general_frame

    def _build_todo_frame(self) -> QWidget:
        """Build the bottom frame: the TODO count heading and the embedded TODO list."""
        todo_frame = QFrame()
        todo_frame.setObjectName("todo_frame")
        todo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        todo_layout = QVBoxLayout(todo_frame)

        self._todo_title_label = QLabel()
        self._todo_title_label.setObjectName("todo_title_label")
        todo_layout.addWidget(self._todo_title_label)
        todo_layout.addWidget(self._todo_list_view, 1)

        return todo_frame

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
        """Surface a failed action to the user."""
        if rs.error_code is not None:
            QMessageBox.warning(self, i18n_fra.DIALOG_ERROR_TITLE, rs.error_code.message)

    def clear(self) -> None:
        """Empty the displayed content."""
        self._name_label.clear()
        self._duration_label.clear()
        self._sound_label.clear()
        self._todo_title_label.clear()

    def notify_refresh(self, context: PomodoroDetailViewState) -> None:
        """Display `context`'s current values."""
        self._name_label.setText(context.name)
        duration_text = format_duration(context.duration_seconds)
        self._duration_label.setText(f"{i18n_fra.FORM_FIELD_DURATION} : {duration_text}")
        self._sound_label.setText(self._format_sound_summary(context))
        self._todo_title_label.setText(i18n_fra.TODO_LIST_TITLE_TEMPLATE.format(count=context.todo_count))

    @staticmethod
    def _format_sound_summary(context: PomodoroDetailViewState) -> str:
        """Format the 'Son : ... — Volume ...% — x... rép.' summary line (spec §2.2)."""
        if context.sound_path is None:
            return i18n_fra.FORM_NO_SOUND_HINT
        fl_name = Path(context.sound_path).name
        return (
            f"{i18n_fra.FORM_FIELD_SOUND} : {fl_name}\n"
            f"{i18n_fra.FORM_FIELD_VOLUME} {context.sound_volume}%\n'"
            f"{i18n_fra.FORM_FIELD_REPEAT} {context.sound_repeat_count}"
        )

    def bind_edit_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '✎' is clicked."""
        self._edit_button.clicked.connect(callback)

    def bind_start_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '▶ Démarrer' is clicked."""
        self._start_button.clicked.connect(callback)


# EOF
