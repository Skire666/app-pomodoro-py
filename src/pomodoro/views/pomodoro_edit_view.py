"""Pomodoro create/edit form (spec §2.3)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Final

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pomodoro.models.app_state_model import AppStateModel
from pomodoro.models.pomodoro_edit_view_state import PomodoroEditViewState
from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared import i18n_fra
from pomodoro.shared.validation_result import ValidationResult

FIELD_CHANGE_DEBOUNCE_MS: Final[int] = 150
SAVED_INDICATOR_DURATION_MS: Final[int] = 1500
SECONDS_PER_HOUR: Final[int] = 3600
SECONDS_PER_MINUTE: Final[int] = 60
VOLUME_PERCENT_MAX: Final[int] = 100


class PomodoroEditView(QWidget):
    """The pomodoro create/edit form: real-time save, live validation (spec §2.3)."""

    def __init__(self, app_state: AppStateModel, parent: QWidget | None = None) -> None:
        """Build the form's widgets and its debounce/saved-indicator timers."""
        super().__init__(parent)
        self.setObjectName("pomodoro_edit_view")
        self._app_state = app_state
        self._on_field_changed: Callable[[], None] | None = None
        self._media_player: QMediaPlayer | None = None
        self._audio_output: QAudioOutput | None = None
        self._debounce_timer = self._make_timer(FIELD_CHANGE_DEBOUNCE_MS, self._emit_field_changed)
        self._saved_indicator_timer = self._make_timer(SAVED_INDICATOR_DURATION_MS, self._hide_saved_indicator)
        self._build_ui()

    def _make_timer(self, interval_ms: int, on_timeout: Callable[[], None]) -> QTimer:
        """Build a single-shot QTimer wired to `on_timeout` (AGENTS.md §16.6)."""
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(interval_ms)
        timer.timeout.connect(on_timeout)
        return timer

    def _build_ui(self) -> None:
        """Lay out every form field and the footer."""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(i18n_fra.FORM_FIELD_NAME))
        self._name_edit = QLineEdit()
        self._name_edit.setObjectName("name_edit")
        self._name_edit.textChanged.connect(self._restart_debounce)
        layout.addWidget(self._name_edit)

        layout.addLayout(self._build_duration_fields())
        layout.addLayout(self._build_sound_fields())
        layout.addLayout(self._build_volume_field())
        layout.addLayout(self._build_repeat_fields())

        layout.addLayout(self._build_footer())

    def _build_duration_fields(self) -> QHBoxLayout:
        """Build the hours/minutes/seconds duration spin boxes (spec §2.3)."""
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel(i18n_fra.FORM_FIELD_DURATION))
        self._hours_spin = self._add_labeled_spinbox(duration_layout, 0, 23, i18n_fra.FORM_DURATION_HOURS_SUFFIX)
        self._minutes_spin = self._add_labeled_spinbox(
            duration_layout, 0, 59, i18n_fra.FORM_DURATION_MINUTES_SUFFIX
        )
        self._seconds_spin = self._add_labeled_spinbox(
            duration_layout, 0, 59, i18n_fra.FORM_DURATION_SECONDS_SUFFIX
        )
        return duration_layout

    def _add_labeled_spinbox(self, layout: QHBoxLayout, minimum: int, maximum: int, suffix: str) -> QSpinBox:
        """Add a `QSpinBox` followed by its unit suffix label to `layout`."""
        spin_box = QSpinBox()
        spin_box.setRange(minimum, maximum)
        spin_box.setFixedSize(100, spin_box.sizeHint().height())
        spin_box.valueChanged.connect(self._restart_debounce)
        layout.addWidget(spin_box)
        layout.addWidget(QLabel(suffix))
        return spin_box

    def _build_sound_fields(self) -> QHBoxLayout:
        """Build the sound selector, browse, and test buttons (spec §2.3)."""
        sound_layout = QHBoxLayout()
        self._sound_combo = QComboBox()
        self._sound_combo.setObjectName("sound_combo")
        self._sound_combo.setEditable(True)
        self._sound_combo.currentTextChanged.connect(self._restart_debounce)
        sound_layout.addWidget(self._sound_combo, 1)

        self._browse_button = QPushButton(i18n_fra.FORM_BUTTON_BROWSE)
        self._browse_button.setObjectName("browse_button")
        self._browse_button.clicked.connect(self._handle_browse_clicked)
        sound_layout.addWidget(self._browse_button)

        self._test_sound_button = QPushButton(i18n_fra.FORM_BUTTON_TEST_SOUND)
        self._test_sound_button.setObjectName("test_sound_button")
        sound_layout.addWidget(self._test_sound_button)
        return sound_layout

    def _build_volume_field(self) -> QHBoxLayout:
        """Build the volume slider and its live percentage label."""
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel(i18n_fra.FORM_FIELD_VOLUME))
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setObjectName("volume_slider")
        self._volume_slider.setRange(0, VOLUME_PERCENT_MAX)
        self._volume_slider.valueChanged.connect(self._restart_debounce)
        volume_layout.addWidget(self._volume_slider, 1)
        self._volume_percent_label = QLabel()
        self._volume_slider.valueChanged.connect(lambda value: self._volume_percent_label.setText(f"{value}%"))
        volume_layout.addWidget(self._volume_percent_label)
        return volume_layout

    def _build_repeat_fields(self) -> QHBoxLayout:
        """Build the repeat-count and repeat-interval spin boxes (spec §2.3)."""
        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel(i18n_fra.FORM_FIELD_REPEAT))
        self._repeat_count_spin = self._add_labeled_spinbox(
            repeat_layout, 1, 50, i18n_fra.FORM_REPEAT_COUNT_SUFFIX
        )
        self._repeat_interval_spin = self._add_labeled_spinbox(
            repeat_layout, 1, 600, i18n_fra.FORM_REPEAT_INTERVAL_SUFFIX
        )
        return repeat_layout

    def _build_footer(self) -> QHBoxLayout:
        """Build the saved indicator and the 'Fermer' button."""
        footer_layout = QHBoxLayout()
        self._saved_label = QLabel(i18n_fra.FORM_SAVED_INDICATOR)
        self._saved_label.setObjectName("saved_label")
        self._saved_label.setVisible(False)
        footer_layout.addWidget(self._saved_label, 1)

        self._close_button = QPushButton(i18n_fra.FORM_CLOSE_BUTTON)
        self._close_button.setObjectName("close_button")
        footer_layout.addWidget(self._close_button)
        return footer_layout

    @property
    def is_dirty(self) -> bool:
        """True while the debounce timer is pending an unsaved edit."""
        return self._debounce_timer.isActive()

    @property
    def is_busy(self) -> bool:
        """This form performs no long-running work of its own."""
        return False

    @property
    def is_loading(self) -> bool:
        """This form has no separate loading phase after construction."""
        return False

    def snapshot(self) -> PomodoroEditViewState:
        """Return the current form field values."""
        sound_text = self._sound_combo.currentText().strip()
        return PomodoroEditViewState(
            name=self._name_edit.text(),
            duration_seconds=self._duration_seconds(),
            sound_path=sound_text or None,
            sound_volume=self._volume_slider.value(),
            sound_repeat_count=self._repeat_count_spin.value(),
            sound_repeat_interval_seconds=self._repeat_interval_spin.value(),
        )

    def _duration_seconds(self) -> int:
        """Combine the hours/minutes/seconds spin boxes into a total duration."""
        return (
            self._hours_spin.value() * SECONDS_PER_HOUR
            + self._minutes_spin.value() * SECONDS_PER_MINUTE
            + self._seconds_spin.value()
        )

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole form."""
        self.setEnabled(enabled)

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed validation or action to the user."""
        if rs.error_code is not None:
            QMessageBox.warning(self, i18n_fra.DIALOG_ERROR_TITLE, rs.error_code.message)

    def clear(self) -> None:
        """Empty every form field."""
        self._name_edit.clear()
        self._hours_spin.setValue(0)
        self._minutes_spin.setValue(0)
        self._seconds_spin.setValue(0)
        self._sound_combo.clearEditText()
        self._volume_slider.setValue(0)
        self._repeat_count_spin.setValue(1)
        self._repeat_interval_spin.setValue(1)

    def notify_refresh(self, context: PomodoroModel) -> None:
        """Populate the form with `context`'s current values."""
        self._name_edit.setText(context.name)
        hours, remainder = divmod(context.duration_seconds, SECONDS_PER_HOUR)
        minutes, seconds = divmod(remainder, SECONDS_PER_MINUTE)
        self._hours_spin.setValue(hours)
        self._minutes_spin.setValue(minutes)
        self._seconds_spin.setValue(seconds)
        self._sound_combo.setCurrentText(context.sound_path or "")
        self._volume_slider.setValue(context.sound_volume)
        self._repeat_count_spin.setValue(context.sound_repeat_count)
        self._repeat_interval_spin.setValue(context.sound_repeat_interval_seconds)

    def notify_saved(self) -> None:
        """Briefly show the '✓ Enregistré' indicator (spec §2.3)."""
        self._saved_label.setVisible(True)
        self._saved_indicator_timer.start()

    def _hide_saved_indicator(self) -> None:
        """Hide the saved indicator once its timer elapses."""
        self._saved_label.setVisible(False)

    def play_preview(self, sound_path: str, volume: int) -> None:
        """Play a short preview of `sound_path` at `volume` (spec §2.3 'Tester')."""
        if self._media_player is None or self._audio_output is None:
            self._media_player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._media_player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(volume / VOLUME_PERCENT_MAX)
        self._media_player.setSource(QUrl.fromLocalFile(sound_path))
        self._media_player.play()

    def _handle_browse_clicked(self) -> None:
        """Open a native file dialog and select the chosen sound (spec §2.3)."""
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self, i18n_fra.FORM_BUTTON_BROWSE, "", i18n_fra.FORM_SOUND_FILE_FILTER
        )
        if file_path:
            self._sound_combo.setCurrentText(file_path)

    def _restart_debounce(self, *_args: object) -> None:
        """Restart the ~400 ms debounce before the next real-time save (spec §3.1)."""
        self._debounce_timer.start()
        self._app_state.set_dirty(self.objectName(), True)

    def _emit_field_changed(self) -> None:
        """Notify the presenter once the debounce settles."""
        self._app_state.set_dirty(self.objectName(), False)
        if self._on_field_changed is not None:
            self._on_field_changed()

    def bind_field_changed(self, callback: Callable[[], None]) -> None:
        """Register the callback fired once the view's own debounce settles."""
        self._on_field_changed = callback

    def bind_test_sound_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Tester' is clicked."""
        self._test_sound_button.clicked.connect(callback)

    def bind_close_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Fermer' is clicked."""
        self._close_button.clicked.connect(callback)


# EOF
