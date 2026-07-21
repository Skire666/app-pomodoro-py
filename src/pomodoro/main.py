"""Application entry point and composition root (AGENTS.md §9)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QStyle, QSystemTrayIcon

from pomodoro.models.app_config_model import AppConfigModel
from pomodoro.models.app_state_model import AppStateModel
from pomodoro.presenters.active_session_presenter import ActiveSessionPresenter
from pomodoro.presenters.history_presenter import HistoryPresenter
from pomodoro.presenters.pomodoro_detail_presenter import PomodoroDetailPresenter
from pomodoro.presenters.pomodoro_edit_presenter import PomodoroEditPresenter
from pomodoro.presenters.pomodoro_list_presenter import PomodoroListPresenter
from pomodoro.presenters.todo_list_presenter import TodoListPresenter
from pomodoro.repositories.config_repository import ConfigRepository
from pomodoro.repositories.sound_repository import SoundRepository
from pomodoro.services.history_service import HistoryService
from pomodoro.services.pomodoro_service import PomodoroService
from pomodoro.services.session_service import SessionService
from pomodoro.services.sound_service import SoundService
from pomodoro.services.todo_service import TodoService
from pomodoro.shared import i18n_fra
from pomodoro.views.active_session_view import ActiveSessionView
from pomodoro.views.history_view import HistoryView
from pomodoro.views.main_window_view import MainWindowView
from pomodoro.views.pomodoro_detail_view import PomodoroDetailView
from pomodoro.views.pomodoro_edit_view import PomodoroEditView
from pomodoro.views.pomodoro_list_view import PomodoroListView
from pomodoro.views.todo_list_view import TodoListView

CONFIG_FILE_PATH = Path("config-pomodoro.json")
LOG_DIRECTORY = Path("tmp_app_logs")
MAIN_WINDOW_INITIAL_WIDTH = 848
MAIN_WINDOW_INITIAL_HEIGHT = 450
DEFAULT_FONT_POINT_SIZE = 12


def _configure_font(app: QApplication) -> None:
    """Apply a single, uniform font size across every widget in the app.

    Set once on the `QApplication` default font rather than per-widget, so
    every screen inherits the same size unless a widget explicitly
    overrides it.
    """
    font = app.font()
    font.setPointSize(DEFAULT_FONT_POINT_SIZE)
    app.setFont(font)


def _configure_logging() -> None:
    """Configure the root logger to write to `./tmp_app_logs/` (AGENTS.md §5, §11)."""
    LOG_DIRECTORY.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_DIRECTORY / "pomodoro.log", encoding="utf-8"), logging.StreamHandler()],
    )


def _build_tray_icon(app: QApplication) -> QSystemTrayIcon:
    """Build the desktop-notification tray icon (spec §3.2), if the OS supports one."""
    tray_icon = QSystemTrayIcon(app)
    tray_icon.setIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray_icon.show()
    return tray_icon


def _make_start_edit(main_window: MainWindowView, edit_presenter: PomodoroEditPresenter) -> Callable[[str], None]:
    """Build the shared 'start editing this pomodoro' callback (spec §2.2, §2.4 'Edit')."""

    def _start_edit(id_pomodoro: str) -> None:
        edit_presenter.start_edit(id_pomodoro)
        main_window.show_edit_form()

    return _start_edit


def _wire_navigation(
    *,
    main_window: MainWindowView,
    pomodoro_list_presenter: PomodoroListPresenter,
    edit_presenter: PomodoroEditPresenter,
    detail_presenter: PomodoroDetailPresenter,
    detail_todo_list_presenter: TodoListPresenter,
    history_presenter: HistoryPresenter,
    start_edit: Callable[[str], None],
) -> None:
    """Wire cross-presenter navigation callbacks (AGENTS.md §9 composition root).

    Selecting a card in the list no longer shows the detail screen (spec
    change): only 'Play', 'Edit', and 'Del.' change the main content area.
    The detail screen itself stays fully wired (including its own 'Edit'
    and its embedded TODO list) for whenever it is reached again.
    """

    def _start_create() -> None:
        edit_presenter.start_create()
        main_window.show_edit_form()

    def _close_edit() -> None:
        pomodoro_list_presenter.refresh()
        detail_presenter.refresh()
        detail_todo_list_presenter.refresh()
        main_window.show_pomodoros_area()

    pomodoro_list_presenter.bind_edit_requested(start_edit)
    pomodoro_list_presenter.bind_new_requested(_start_create)
    detail_presenter.bind_edit_requested(start_edit)
    edit_presenter.bind_closed(_close_edit)
    main_window.bind_history_nav_clicked(history_presenter.refresh)
    main_window.bind_pomodoros_nav_clicked(pomodoro_list_presenter.refresh)


def _wire_session(  # foqa: EPI025 -- composition root wiring, AGENTS.md §9
    *,
    main_window: MainWindowView,
    session_service: SessionService,
    pomodoro_list_presenter: PomodoroListPresenter,
    detail_presenter: PomodoroDetailPresenter,
    session_todo_list_presenter: TodoListPresenter,
    session_presenter: ActiveSessionPresenter,
    start_edit: Callable[[str], None],
) -> None:
    """Wire the 'Démarrer'/switch flows for the active session (spec §2.4)."""

    def _show_session(id_pomodoro: str) -> None:
        session_todo_list_presenter.show_for_pomodoro(id_pomodoro)
        session_presenter.show()
        main_window.show_session()

    def _start_session(id_pomodoro: str) -> None:
        active = session_service.get_active()
        if active is not None and active.id_pomodoro == id_pomodoro:
            _show_session(id_pomodoro)
            return
        if active is not None:
            if not active.is_paused:
                message = i18n_fra.SESSION_SWITCH_CONFIRM_TEMPLATE.format(name=active.name_snapshot)
                answer = QMessageBox.question(main_window, i18n_fra.DIALOG_CONFIRM_TITLE, message)
                if answer != QMessageBox.StandardButton.Yes:
                    return
            session_presenter.stop_ringing()
            session_service.stop_interrupted()
        result = session_service.start(id_pomodoro)
        if not result.is_valid:
            if result.error_code is not None:
                QMessageBox.warning(main_window, i18n_fra.DIALOG_ERROR_TITLE, result.error_code.message)
            return
        pomodoro_list_presenter.refresh()
        _show_session(id_pomodoro)

    pomodoro_list_presenter.bind_start_requested(_start_session)
    detail_presenter.bind_start_requested(_start_session)
    session_presenter.bind_edit_requested(start_edit)


def main() -> int:  # foqa: EPI025 -- composition root assembles every layer once, AGENTS.md §9
    """Assemble every layer exactly once and run the Qt event loop.

    Returns:
        The process exit code from the Qt event loop.
    """
    _configure_logging()
    app = QApplication(sys.argv)
    _configure_font(app)
    _build_tray_icon(app)

    config_repository = ConfigRepository(CONFIG_FILE_PATH)
    AppConfigModel.set_instance(config_repository.load())
    sound_repository = SoundRepository()
    app_state = AppStateModel()

    pomodoro_service = PomodoroService(config_repository)
    todo_service = TodoService(config_repository)
    history_service = HistoryService(config_repository)
    sound_service = SoundService(sound_repository)
    session_service = SessionService(config_repository)
    if session_service.get_active() is not None:
        session_service.stop_interrupted()

    detail_todo_list_view = TodoListView(app_state, "detail_todo_list_view")
    detail_todo_list_presenter = TodoListPresenter(detail_todo_list_view, todo_service)

    session_todo_list_view = TodoListView(app_state, "session_todo_list_view")
    session_todo_list_presenter = TodoListPresenter(session_todo_list_view, todo_service)

    pomodoro_list_view = PomodoroListView()
    pomodoro_list_presenter = PomodoroListPresenter(pomodoro_list_view, pomodoro_service)

    detail_view = PomodoroDetailView(detail_todo_list_view)
    detail_presenter = PomodoroDetailPresenter(detail_view, pomodoro_service, todo_service)

    edit_view = PomodoroEditView(app_state)
    edit_presenter = PomodoroEditPresenter(edit_view, pomodoro_service, sound_service)

    session_view = ActiveSessionView(session_todo_list_view)
    session_presenter = ActiveSessionPresenter(session_view, session_service, pomodoro_service)

    history_view = HistoryView()
    history_presenter = HistoryPresenter(history_view, history_service, pomodoro_service)

    main_window = MainWindowView(pomodoro_list_view, detail_view, edit_view, session_view, history_view)
    start_edit = _make_start_edit(main_window, edit_presenter)
    _wire_navigation(
        main_window=main_window,
        pomodoro_list_presenter=pomodoro_list_presenter,
        edit_presenter=edit_presenter,
        detail_presenter=detail_presenter,
        detail_todo_list_presenter=detail_todo_list_presenter,
        history_presenter=history_presenter,
        start_edit=start_edit,
    )
    _wire_session(
        main_window=main_window,
        session_service=session_service,
        pomodoro_list_presenter=pomodoro_list_presenter,
        detail_presenter=detail_presenter,
        session_todo_list_presenter=session_todo_list_presenter,
        session_presenter=session_presenter,
        start_edit=start_edit,
    )

    pomodoro_list_presenter.refresh()

    main_window.resize(MAIN_WINDOW_INITIAL_WIDTH, MAIN_WINDOW_INITIAL_HEIGHT)
    main_window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


# EOF
