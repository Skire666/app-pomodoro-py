"""Left-column pomodoro list screen (spec §2.1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from pomodoro.models.pomodoro_list_view_state import PomodoroListViewState
from pomodoro.models.pomodoro_row_state import PomodoroRowState
from pomodoro.shared import i18n_fra
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.validation_result import ValidationResult
from pomodoro.views.pomodoro_card_widget import PomodoroCardWidget

_SORT_MODES: tuple[tuple[str, PomodoroSortModeEnum], ...] = (
    (i18n_fra.LIST_SORT_NAME, PomodoroSortModeEnum.E_NAME),
    (i18n_fra.LIST_SORT_DURATION, PomodoroSortModeEnum.E_DURATION),
    (i18n_fra.LIST_SORT_LAST_USED, PomodoroSortModeEnum.E_LAST_USED),
)


class PomodoroListView(QWidget):
    """Left-column pomodoro list: search, sort, and quick actions (spec §2.1)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the list screen's widgets."""
        super().__init__(parent)
        self.setObjectName("pomodoro_list_view")
        self._on_item_start_clicked: Callable[[str], None] | None = None
        self._on_item_edit_clicked: Callable[[str], None] | None = None
        self._on_item_duplicate_clicked: Callable[[str], None] | None = None
        self._on_item_delete_clicked: Callable[[str], None] | None = None
        self._build_ui()
        self._build_shortcuts()

    def _build_ui(self) -> None:
        """Lay out the search/sort controls, card list, and empty state."""
        layout = QVBoxLayout(self)
        layout.addLayout(self._build_top_controls())
        layout.addLayout(self._build_sort_controls())

        self._empty_state_widget = self._build_empty_state_widget()
        layout.addWidget(self._empty_state_widget)

        self._cards_container = QWidget()
        self._cards_container.setObjectName("cards_container")
        self._cards_layout = QVBoxLayout(self._cards_container)
        scroll_area = QScrollArea()
        scroll_area.setObjectName("cards_scroll_area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self._cards_container)
        layout.addWidget(scroll_area, 1)

    def _build_top_controls(self) -> QHBoxLayout:
        """Build the search field and '+ Nouveau' button."""
        top_layout = QHBoxLayout()
        self._search_edit = QLineEdit()
        self._search_edit.setObjectName("search_edit")
        self._search_edit.setPlaceholderText(i18n_fra.TOP_BAR_SEARCH_PLACEHOLDER)
        top_layout.addWidget(self._search_edit, 1)

        self._new_button = QPushButton(i18n_fra.TOP_BAR_NEW_BUTTON)
        self._new_button.setObjectName("new_button")
        top_layout.addWidget(self._new_button)
        return top_layout

    def _build_sort_controls(self) -> QHBoxLayout:
        """Build the sort selector."""
        sort_layout = QHBoxLayout()
        self._sort_combo = QComboBox()
        self._sort_combo.setObjectName("sort_combo")
        for label, _mode in _SORT_MODES:
            self._sort_combo.addItem(label)
        sort_layout.addWidget(self._sort_combo)
        return sort_layout

    def _build_empty_state_widget(self) -> QWidget:
        """Build the 'Aucun pomodoro pour l'instant' placeholder (spec §2.1)."""
        empty_state_widget = QWidget()
        empty_state_widget.setObjectName("empty_state_widget")
        empty_state_layout = QVBoxLayout(empty_state_widget)
        message_label = QLabel(i18n_fra.LIST_EMPTY_MESSAGE)
        message_label.setObjectName("empty_state_message_label")
        empty_state_layout.addWidget(message_label)

        self._empty_state_new_button = QPushButton(i18n_fra.LIST_EMPTY_CREATE_BUTTON)
        self._empty_state_new_button.setObjectName("empty_state_new_button")
        empty_state_layout.addWidget(self._empty_state_new_button)

        empty_state_widget.setVisible(False)
        return empty_state_widget

    def _build_shortcuts(self) -> None:
        """Wire 'Ctrl+N' (new pomodoro) and 'Ctrl+F' (focus search) (spec §3.3)."""
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self._new_button.click)
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._search_edit.setFocus)

    @property
    def is_dirty(self) -> bool:
        """This browse-only screen never holds an unsaved edit."""
        return False

    @property
    def is_busy(self) -> bool:
        """This screen performs no long-running work of its own."""
        return False

    @property
    def is_loading(self) -> bool:
        """This screen has no separate loading phase after construction."""
        return False

    def snapshot(self) -> PomodoroListViewState:
        """Return the current search/sort controls."""
        return PomodoroListViewState(
            search_text=self._search_edit.text(),
            sort_mode=self._current_sort_mode(),
        )

    def _current_sort_mode(self) -> PomodoroSortModeEnum:
        """Resolve the sort combo's current selection to a `PomodoroSortModeEnum`."""
        index = self._sort_combo.currentIndex()
        if 0 <= index < len(_SORT_MODES):
            return _SORT_MODES[index][1]
        return PomodoroSortModeEnum.E_UNSET

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole list."""
        self.setEnabled(enabled)

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed action to the user."""
        if rs.error_code is not None:
            QMessageBox.warning(self, i18n_fra.DIALOG_ERROR_TITLE, rs.error_code.message)

    def clear(self) -> None:
        """Empty the in-memory list content."""
        self._clear_cards()
        self._search_edit.clear()

    def notify_refresh(self, context: tuple[PomodoroRowState, ...]) -> None:
        """Replace the displayed rows with `context`."""
        self._clear_cards()
        is_empty = not context
        self._empty_state_widget.setVisible(is_empty)
        self._cards_container.setVisible(not is_empty)
        for row in context:
            self._add_card(row)

    def _add_card(self, row: PomodoroRowState) -> None:
        """Create one card for `row` and wire its signals to the registered callbacks."""
        card = PomodoroCardWidget(row, self._cards_container)
        if self._on_item_start_clicked is not None:
            card.start_clicked.connect(self._on_item_start_clicked)
        if self._on_item_edit_clicked is not None:
            card.edit_clicked.connect(self._on_item_edit_clicked)
        if self._on_item_duplicate_clicked is not None:
            card.duplicate_clicked.connect(self._on_item_duplicate_clicked)
        if self._on_item_delete_clicked is not None:
            card.delete_clicked.connect(self._on_item_delete_clicked)
        self._cards_layout.addWidget(card)

    def _clear_cards(self) -> None:
        """Remove and schedule deletion of every currently displayed card."""
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def bind_search_changed(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when the search text changes."""
        self._search_edit.textChanged.connect(callback)

    def bind_sort_changed(self, callback: Callable[[PomodoroSortModeEnum], None]) -> None:
        """Register the callback fired when the sort selector changes."""

        def _on_index_changed(index: int) -> None:
            callback(_SORT_MODES[index][1] if 0 <= index < len(_SORT_MODES) else PomodoroSortModeEnum.E_UNSET)

        self._sort_combo.currentIndexChanged.connect(_on_index_changed)

    def bind_new_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when '+ Nouveau' is clicked."""
        self._new_button.clicked.connect(callback)
        self._empty_state_new_button.clicked.connect(callback)

    def bind_item_start_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Démarrer' action is clicked."""
        self._on_item_start_clicked = callback

    def bind_item_edit_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Modifier' action is clicked."""
        self._on_item_edit_clicked = callback

    def bind_item_duplicate_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Dupliquer' action is clicked."""
        self._on_item_duplicate_clicked = callback

    def bind_item_delete_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a card's 'Supprimer' action is clicked."""
        self._on_item_delete_clicked = callback


# EOF
