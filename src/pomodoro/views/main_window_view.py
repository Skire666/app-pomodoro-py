"""Top-level application window: left navigation and main content area (spec §1)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from pomodoro.shared import i18n_fra


class MainWindowView(QMainWindow):
    """The single top-level window: left nav + pomodoro list, and a main content area.

    The main content area is a `QStackedWidget` cycling between an empty
    placeholder, the pomodoro detail screen, the create/edit form, the
    active-session screen, and the history screen (spec §1: "zone
    principale : change de contenu selon le contexte"). Switching pages
    never stops the session screen's own timer, so a running countdown
    keeps ticking in the background while another page is shown (spec
    §2.4: "Si l'app est minimisée ou en arrière-plan, le son joue quand
    même").
    """

    def __init__(
        self,
        pomodoro_list_view: QWidget,
        detail_view: QWidget,
        edit_view: QWidget,
        session_view: QWidget,
        history_view: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        """Assemble the window from its already-built child views."""
        super().__init__(parent)
        self.setObjectName("main_window_view")
        self.setWindowTitle(i18n_fra.APP_WINDOW_TITLE)
        self._detail_view = detail_view
        self._edit_view = edit_view
        self._session_view = session_view
        self._history_view = history_view
        self._on_pomodoros_nav_clicked: Callable[[], None] | None = None
        self._on_history_nav_clicked: Callable[[], None] | None = None
        self._build_ui(pomodoro_list_view)
        self._last_pomodoro_widget = self._empty_page

    def _build_ui(self, pomodoro_list_view: QWidget) -> None:
        """Lay out the left panel and the main content stack."""
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        root_layout = QHBoxLayout(central_widget)

        root_layout.addLayout(self._build_left_panel(pomodoro_list_view), 1)

        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("content_stack")
        self._empty_page = QWidget()
        self._empty_page.setObjectName("empty_page")
        self._content_stack.addWidget(self._empty_page)
        self._content_stack.addWidget(self._detail_view)
        self._content_stack.addWidget(self._edit_view)
        self._content_stack.addWidget(self._session_view)
        self._content_stack.addWidget(self._history_view)
        root_layout.addWidget(self._content_stack, 1)

        self.setCentralWidget(central_widget)

    def _build_left_panel(self, pomodoro_list_view: QWidget) -> QVBoxLayout:
        """Build the 'Pomodoros'/'Historique' nav row above the pomodoro list."""
        left_layout = QVBoxLayout()
        nav_layout = QHBoxLayout()

        self._pomodoros_nav_button = QPushButton(i18n_fra.NAV_POMODOROS)
        self._pomodoros_nav_button.setObjectName("pomodoros_nav_button")
        self._pomodoros_nav_button.setCheckable(True)
        self._pomodoros_nav_button.setChecked(True)
        self._pomodoros_nav_button.clicked.connect(self._handle_pomodoros_nav_clicked)
        nav_layout.addWidget(self._pomodoros_nav_button)

        self._history_nav_button = QPushButton(i18n_fra.NAV_HISTORY)
        self._history_nav_button.setObjectName("history_nav_button")
        self._history_nav_button.setCheckable(True)
        self._history_nav_button.clicked.connect(self._handle_history_nav_clicked)
        nav_layout.addWidget(self._history_nav_button)

        left_layout.addLayout(nav_layout)
        left_layout.addWidget(pomodoro_list_view, 1)
        return left_layout

    def _handle_pomodoros_nav_clicked(self) -> None:
        """Switch back to the pomodoro area and notify the composition root."""
        self._history_nav_button.setChecked(False)
        self._pomodoros_nav_button.setChecked(True)
        self._content_stack.setCurrentWidget(self._last_pomodoro_widget)
        if self._on_pomodoros_nav_clicked is not None:
            self._on_pomodoros_nav_clicked()

    def _handle_history_nav_clicked(self) -> None:
        """Switch to the history screen and notify the composition root."""
        self._pomodoros_nav_button.setChecked(False)
        self._history_nav_button.setChecked(True)
        self._content_stack.setCurrentWidget(self._history_view)
        if self._on_history_nav_clicked is not None:
            self._on_history_nav_clicked()

    def show_detail(self) -> None:
        """Switch the main content area to the read-only detail screen."""
        self._last_pomodoro_widget = self._detail_view
        self._content_stack.setCurrentWidget(self._detail_view)

    def show_edit_form(self) -> None:
        """Switch the main content area to the create/edit form."""
        self._content_stack.setCurrentWidget(self._edit_view)

    def show_session(self) -> None:
        """Switch the main content area to the active-session screen (spec §2.4)."""
        self._last_pomodoro_widget = self._session_view
        self._content_stack.setCurrentWidget(self._session_view)

    def show_pomodoros_area(self) -> None:
        """Return to whichever pomodoro page (empty or detail) was last active."""
        self._content_stack.setCurrentWidget(self._last_pomodoro_widget)

    def bind_pomodoros_nav_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when the 'Pomodoros' nav button is clicked."""
        self._on_pomodoros_nav_clicked = callback

    def bind_history_nav_clicked(self, callback: Callable[[], None]) -> None:
        """Register the callback fired when the 'Historique' nav button is clicked."""
        self._on_history_nav_clicked = callback


# EOF
