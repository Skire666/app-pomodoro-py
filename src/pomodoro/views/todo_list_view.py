"""A pomodoro's TODO list screen (spec §2.5)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable
from typing import Final

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from pomodoro.models.app_state_model import AppStateModel
from pomodoro.models.todo_row_state import TodoRowState
from pomodoro.shared import i18n_fra
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.validation_result import ValidationResult
from pomodoro.views.todo_table_model import STATE_LABELS, TodoTableModel

UNDO_TOAST_DURATION_MS: Final[int] = 5000
DEFAULT_OBJECT_NAME: Final[str] = "todo_list_view"


class TodoListView(QWidget):
    """A pomodoro's TODO list: inline label edit, context-menu actions (spec §2.5).

    State changes, duplication, and deletion are exposed through a
    right-click context menu rather than per-row hover icons, which are
    impractical to implement reliably inside a `QTableView` cell.
    """

    def __init__(
        self,
        app_state: AppStateModel,
        object_name: str = DEFAULT_OBJECT_NAME,
        parent: QWidget | None = None,
    ) -> None:
        """Build the list's widgets and its undo-toast timer.

        Args:
            app_state: The shared application state to propagate `is_dirty` into.
            object_name: Unique widget name, also used as the `AppStateModel`
                holder key: pass a distinct value per instance when this view
                is embedded more than once (spec §2.2 detail tab, §2.4 session).
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setObjectName(object_name)
        self._app_state = app_state
        self._on_add_item_requested: Callable[[str], None] | None = None
        self._on_item_state_changed: Callable[[str, TodoStateEnum], None] | None = None
        self._on_item_duplicate_clicked: Callable[[str], None] | None = None
        self._on_item_delete_clicked: Callable[[str], None] | None = None
        self._on_delete_list_clicked: Callable[[], None] | None = None
        self._undo_timer = QTimer(self)
        self._undo_timer.setSingleShot(True)
        self._undo_timer.setInterval(UNDO_TOAST_DURATION_MS)
        self._undo_timer.timeout.connect(self._hide_toast)
        self._build_ui()

    def _build_ui(self) -> None:
        """Lay out the table, the add-item field, the toast, and the delete-list button."""
        layout = QVBoxLayout(self)

        self._table_model = TodoTableModel(self)
        self._table_view = QTableView()
        self._table_view.setObjectName("table_view")
        self._table_view.setModel(self._table_model)
        self._table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table_view.customContextMenuRequested.connect(self._show_context_menu)
        self._table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table_view, 1)

        self._new_item_edit = QLineEdit()
        self._new_item_edit.setObjectName("new_item_edit")
        self._new_item_edit.setPlaceholderText(i18n_fra.TODO_ADD_LINE_BUTTON)
        self._new_item_edit.returnPressed.connect(self._handle_new_item_submitted)
        self._new_item_edit.textChanged.connect(self._handle_new_item_text_changed)
        layout.addWidget(self._new_item_edit)

        layout.addWidget(self._build_toast_widget())

        self._delete_list_button = QPushButton(i18n_fra.TODO_DELETE_LIST_BUTTON)
        self._delete_list_button.setObjectName("delete_list_button")
        self._delete_list_button.clicked.connect(self._handle_delete_list_clicked)
        layout.addWidget(self._delete_list_button)

    def _build_toast_widget(self) -> QWidget:
        """Build the 'Ligne supprimée — Annuler' toast (spec §2.5)."""
        toast_widget = QWidget()
        toast_widget.setObjectName("toast_widget")
        toast_layout = QHBoxLayout(toast_widget)
        toast_layout.setContentsMargins(0, 0, 0, 0)
        self._toast_label = QLabel()
        self._toast_label.setObjectName("toast_label")
        toast_layout.addWidget(self._toast_label, 1)
        self._undo_button = QPushButton(i18n_fra.TODO_UNDO_BUTTON)
        self._undo_button.setObjectName("undo_button")
        self._undo_button.clicked.connect(self._hide_toast)
        toast_layout.addWidget(self._undo_button)
        toast_widget.setVisible(False)
        self._toast_widget = toast_widget
        return toast_widget

    def _show_context_menu(self, position: QPoint) -> None:
        """Show the per-row 'Changer l'état'/'Dupliquer'/'Supprimer' menu (spec §2.5)."""
        index = self._table_view.indexAt(position)
        row = self._table_model.row_at(index.row())
        if row is None:
            return
        menu = QMenu(self)
        self._populate_state_submenu(menu, row)
        duplicate_action = menu.addAction(i18n_fra.LIST_ACTION_DUPLICATE)
        duplicate_action.triggered.connect(lambda: self._emit_duplicate_clicked(row.id_todo_item))
        delete_action = menu.addAction(i18n_fra.LIST_ACTION_DELETE)
        delete_action.triggered.connect(lambda: self._emit_delete_clicked(row.id_todo_item))
        menu.exec(self._table_view.viewport().mapToGlobal(position))

    def _populate_state_submenu(self, menu: QMenu, row: TodoRowState) -> None:
        """Add the 'Changer l'état' submenu with one action per TODO state."""
        state_menu = menu.addMenu(i18n_fra.TODO_CHANGE_STATE_MENU)
        for state, label in STATE_LABELS.items():
            action = state_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, s=state: self._emit_state_changed(row.id_todo_item, s))

    def _handle_new_item_text_changed(self, text: str) -> None:
        """Propagate whether the new-item field holds unsubmitted text."""
        self._app_state.set_dirty(self.objectName(), bool(text))

    def _handle_new_item_submitted(self) -> None:
        """Submit the pending new-item text, if non-empty (spec §2.5 'Entrée valide')."""
        label = self._new_item_edit.text().strip()
        if not label:
            return
        self._new_item_edit.clear()
        if self._on_add_item_requested is not None:
            self._on_add_item_requested(label)

    def _handle_delete_list_clicked(self) -> None:
        """Confirm, then forward 'Supprimer la liste' (spec §2.5, obligatory confirmation)."""
        message = i18n_fra.TODO_DELETE_LIST_CONFIRM_TEMPLATE.format(count=self._table_model.rowCount())
        answer = QMessageBox.question(self, i18n_fra.DIALOG_CONFIRM_TITLE, message)
        if answer == QMessageBox.StandardButton.Yes and self._on_delete_list_clicked is not None:
            self._on_delete_list_clicked()

    @property
    def is_dirty(self) -> bool:
        """True while the add-item field holds unsubmitted text."""
        return bool(self._new_item_edit.text())

    @property
    def is_busy(self) -> bool:
        """This screen performs no long-running work of its own."""
        return False

    @property
    def is_loading(self) -> bool:
        """This screen has no separate loading phase after construction."""
        return False

    def set_enabled(self, enabled: bool) -> None:
        """Grey out or re-enable the whole list."""
        self.setEnabled(enabled)

    def notify_error(self, rs: ValidationResult) -> None:
        """Surface a failed action to the user."""
        if rs.error_code is not None:
            QMessageBox.warning(self, i18n_fra.DIALOG_ERROR_TITLE, rs.error_code.message)

    def clear(self) -> None:
        """Empty the in-memory list content."""
        self._table_model.set_rows(())
        self._new_item_edit.clear()
        self._hide_toast()

    def notify_refresh(self, context: tuple[TodoRowState, ...]) -> None:
        """Replace the displayed rows with `context`."""
        self._table_model.set_rows(context)

    def notify_item_deleted(self, label: str) -> None:
        """Show the 'Ligne supprimée — Annuler' toast for `label` (spec §2.5)."""
        self._toast_label.setText(f"{i18n_fra.TODO_DELETE_LINE_TOAST} : {label}")
        self._toast_widget.setVisible(True)
        self._undo_timer.start()

    def _hide_toast(self) -> None:
        """Hide the delete-undo toast."""
        self._toast_widget.setVisible(False)

    def bind_add_item_requested(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when a new line is validated (Entrée)."""
        self._on_add_item_requested = callback

    def bind_item_renamed(self, callback: Callable[[str, str], None]) -> None:
        """Register the callback fired when an item's label is edited inline."""
        self._table_model.label_edited.connect(callback)

    def bind_item_state_changed(self, callback: Callable[[str, TodoStateEnum], None]) -> None:
        """Register the callback fired when an item's state is changed via the context menu."""
        self._on_item_state_changed = callback

    def bind_item_duplicate_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when an item's duplicate action is chosen."""
        self._on_item_duplicate_clicked = callback

    def bind_item_delete_clicked(self, callback: Callable[[str], None]) -> None:
        """Register the callback fired when an item's delete action is chosen."""
        self._on_item_delete_clicked = callback

    def bind_delete_list_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when 'Supprimer la liste' is confirmed."""
        self._on_delete_list_clicked = callback

    def bind_undo_delete_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when the delete toast's 'Annuler' is clicked."""
        self._undo_button.clicked.connect(callback)

    def _emit_state_changed(self, id_todo_item: str, state: TodoStateEnum) -> None:
        """Forward a state selection from the context menu to the registered callback."""
        if self._on_item_state_changed is not None:
            self._on_item_state_changed(id_todo_item, state)

    def _emit_duplicate_clicked(self, id_todo_item: str) -> None:
        """Forward a duplicate selection from the context menu to the registered callback."""
        if self._on_item_duplicate_clicked is not None:
            self._on_item_duplicate_clicked(id_todo_item)

    def _emit_delete_clicked(self, id_todo_item: str) -> None:
        """Forward a delete selection from the context menu to the registered callback."""
        if self._on_item_delete_clicked is not None:
            self._on_item_delete_clicked(id_todo_item)


# EOF
