"""Active pomodoro session screen: countdown, Edit/Play/Pause/Reset, TODO list (spec §2.4)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Final

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget

from pomodoro.models.active_session_view_state import ActiveSessionViewState
from pomodoro.shared import i18n_fra
from pomodoro.shared.validation_result import ValidationResult

TICK_INTERVAL_MS: Final[int] = 1000
SECONDS_PER_HOUR: Final[int] = 3600
SECONDS_PER_MINUTE: Final[int] = 60
VOLUME_PERCENT_MAX: Final[int] = 100


def format_countdown(remaining_seconds: int) -> str:
    """Format a countdown as MM:SS, or HH:MM:SS once at least one hour remains (spec §2.4).

    Once the planned duration has elapsed, `remaining_seconds` goes negative
    (spec §2.4 overtime alarm) and is rendered with a leading '-'.
    """
    sign = "-" if remaining_seconds < 0 else ""
    hours, remainder = divmod(abs(remaining_seconds), SECONDS_PER_HOUR)
    minutes, seconds = divmod(remainder, SECONDS_PER_MINUTE)
    if hours > 0:
        return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{sign}{minutes:02d}:{seconds:02d}"


class ActiveSessionView(QWidget):
    """The countdown screen for the currently running pomodoro session (spec §2.4).

    Uses a linear `QProgressBar` in place of the spec's circular progress
    ring: a custom-painted ring cannot be visually verified in this
    environment (AGENTS.md §17), so the simpler, statically-safe widget was
    chosen instead.

    The action row is Edit/Play/Pause/Reset: Play and Pause are always both
    present, and the one matching the current state is disabled instead of
    being swapped out (Play disabled while running, Pause disabled while
    paused).
    """

    def __init__(self, todo_list_view: QWidget, parent: QWidget | None = None) -> None:
        """Build the session screen's widgets, embedding `todo_list_view`."""
        super().__init__(parent)
        self.setObjectName("active_session_view")
        self._planned_duration_seconds = 0
        self._is_paused = False
        self._on_tick_requested: Callable[[], None] | None = None
        self._on_edit_clicked: Callable[[], None] | None = None
        self._media_player: QMediaPlayer | None = None
        self._audio_output: QAudioOutput | None = None
        self._sound_remaining_plays = 0
        self._sound_repeat_interval_ms = 0
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(TICK_INTERVAL_MS)
        self._tick_timer.timeout.connect(self._emit_tick)
        self._build_ui(todo_list_view)
        self._build_shortcuts()

    def _build_ui(self, todo_list_view: QWidget) -> None:
        """Lay out the countdown, progress bar, action row, and TODO list."""
        layout = QVBoxLayout(self)

        self._name_label = QLabel()
        self._name_label.setObjectName("name_label")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._name_label)

        self._countdown_label = QLabel()
        self._countdown_label.setObjectName("countdown_label")
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._countdown_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setObjectName("progress_bar")
        self._progress_bar.setTextVisible(False)
        layout.addWidget(self._progress_bar)

        layout.addLayout(self._build_action_row())

        todo_label = QLabel(i18n_fra.SESSION_TODO_IN_PROGRESS_TITLE)
        todo_label.setObjectName("todo_label")
        layout.addWidget(todo_label)
        layout.addWidget(todo_list_view, 1)

    def _build_action_row(self) -> QHBoxLayout:
        """Build the Edit/Play/Pause/Reset action row, left to right."""
        buttons_layout = QHBoxLayout()

        self._edit_button = QPushButton(i18n_fra.LIST_ACTION_EDIT)
        self._edit_button.setObjectName("edit_button")
        self._edit_button.clicked.connect(self._emit_edit_clicked)
        buttons_layout.addWidget(self._edit_button)

        self._play_button = QPushButton(i18n_fra.LIST_ACTION_START)
        self._play_button.setObjectName("play_button")
        buttons_layout.addWidget(self._play_button)

        self._pause_button = QPushButton(i18n_fra.SESSION_PAUSE_BUTTON)
        self._pause_button.setObjectName("pause_button")
        buttons_layout.addWidget(self._pause_button)

        self._reset_button = QPushButton(i18n_fra.SESSION_RESET_BUTTON)
        self._reset_button.setObjectName("reset_button")
        buttons_layout.addWidget(self._reset_button)

        return buttons_layout

    def _build_shortcuts(self) -> None:
        """Wire 'Espace' to toggle Play/Pause while this screen is active (spec §3.3)."""
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut.activated.connect(self._handle_space_shortcut)

    def _handle_space_shortcut(self) -> None:
        """Click whichever of Play/Pause is currently enabled."""
        if self._is_paused:
            self._play_button.click()
        else:
            self._pause_button.click()

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
        """Reset the screen to its idle, pre-session appearance."""
        self._tick_timer.stop()
        self._name_label.clear()
        self._countdown_label.clear()
        self._progress_bar.setValue(0)

    def notify_refresh(self, context: ActiveSessionViewState) -> None:
        """Display `context`'s current values when the session is first shown."""
        self._name_label.setText(context.name)
        self._planned_duration_seconds = context.planned_duration_seconds
        self._progress_bar.setRange(0, max(1, context.planned_duration_seconds))
        self._update_countdown(context.remaining_seconds, is_paused=context.is_paused)
        self._tick_timer.start()

    def notify_tick(self, remaining_seconds: int, is_paused: bool) -> None:
        """Update the countdown display for one second of elapsed time."""
        self._update_countdown(remaining_seconds, is_paused=is_paused)

    def _update_countdown(self, remaining_seconds: int, *, is_paused: bool) -> None:
        """Refresh the countdown label, progress bar, and Play/Pause enabled state."""
        self._is_paused = is_paused
        self._countdown_label.setText(format_countdown(remaining_seconds))
        elapsed = min(self._planned_duration_seconds, max(0, self._planned_duration_seconds - remaining_seconds))
        self._progress_bar.setValue(elapsed)
        self._play_button.setEnabled(is_paused)
        self._pause_button.setEnabled(not is_paused)

    def play_completion_sound(
        self, sound_path: str, volume: int, repeat_count: int, repeat_interval_seconds: int
    ) -> None:
        """Play the configured completion sound, repeated per the pomodoro's settings."""
        if self._media_player is None or self._audio_output is None:
            self._media_player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._media_player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(volume / VOLUME_PERCENT_MAX)
        self._media_player.setSource(QUrl.fromLocalFile(sound_path))
        self._sound_remaining_plays = max(1, repeat_count)
        self._sound_repeat_interval_ms = repeat_interval_seconds * 1000
        self._play_next_repeat()

    def _play_next_repeat(self) -> None:
        """Play one repetition of the completion sound, scheduling the next if any remain."""
        if self._media_player is None or self._sound_remaining_plays <= 0:
            return
        self._sound_remaining_plays -= 1
        self._media_player.play()
        if self._sound_remaining_plays > 0:
            QTimer.singleShot(self._sound_repeat_interval_ms, self._play_next_repeat)

    def stop_completion_sound(self) -> None:
        """Silence the completion alarm immediately and cancel any pending repetition."""
        self._sound_remaining_plays = 0
        if self._media_player is not None:
            self._media_player.stop()

    def _emit_edit_clicked(self) -> None:
        """Notify the presenter that 'Edit' was clicked."""
        if self._on_edit_clicked is not None:
            self._on_edit_clicked()

    def _emit_tick(self) -> None:
        """Notify the presenter once a second."""
        if self._on_tick_requested is not None:
            self._on_tick_requested()

    def bind_tick_requested(self, callback: Callable[[], None]) -> None:
        """Register the callback fired once a second by the view's own timer."""
        self._on_tick_requested = callback

    def bind_edit_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Edit' is clicked."""
        self._on_edit_clicked = callback

    def bind_play_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Play' is clicked (greyed out while running)."""
        self._play_button.clicked.connect(callback)

    def bind_pause_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '⏸ Pause' is clicked (greyed out while paused)."""
        self._pause_button.clicked.connect(callback)

    def bind_reset_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '⟲ Reset' is clicked."""
        self._reset_button.clicked.connect(callback)


# EOF
