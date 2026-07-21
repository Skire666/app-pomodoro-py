from collections.abc import Callable

from pomodoro.models.todo_row_state import TodoRowState
from pomodoro.presenters.todo_list_presenter import TodoListPresenter
from pomodoro.services.todo_service import TodoService
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.validation_result import ValidationResult
from tests.conftest import FakeConfigRepository


class FakeTodoListView:
    def __init__(self) -> None:
        self.is_dirty = False
        self.is_busy = False
        self.is_loading = False
        self.enabled = True
        self.last_error: ValidationResult | None = None
        self.rows: tuple[TodoRowState, ...] = ()
        self.deleted_toast_label: str | None = None
        self.callbacks: dict[str, Callable[..., None]] = {}

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def notify_error(self, rs: ValidationResult) -> None:
        self.last_error = rs

    def clear(self) -> None:
        self.rows = ()

    def notify_refresh(self, context: tuple[TodoRowState, ...]) -> None:
        self.rows = context

    def notify_item_deleted(self, label: str) -> None:
        self.deleted_toast_label = label

    def bind_add_item_requested(self, callback: Callable[[str], None]) -> None:
        self.callbacks["add_item_requested"] = callback

    def bind_item_renamed(self, callback: Callable[[str, str], None]) -> None:
        self.callbacks["item_renamed"] = callback

    def bind_item_state_changed(self, callback: Callable[[str, TodoStateEnum], None]) -> None:
        self.callbacks["item_state_changed"] = callback

    def bind_item_duplicate_clicked(self, callback: Callable[[str], None]) -> None:
        self.callbacks["item_duplicate_clicked"] = callback

    def bind_item_delete_clicked(self, callback: Callable[[str], None]) -> None:
        self.callbacks["item_delete_clicked"] = callback

    def bind_delete_list_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["delete_list_clicked"] = callback

    def bind_undo_delete_clicked(self, callback: Callable[[], None]) -> None:
        self.callbacks["undo_delete_clicked"] = callback


def test_show_for_pomodoro_loads_the_items_of_that_pomodoro(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    service.add_item("pom-2", "Autre pomodoro")
    presenter = TodoListPresenter(view, service)

    presenter.show_for_pomodoro("pom-1")

    assert [row.label for row in view.rows] == ["Ecrire le brief"]


def test_add_item_requested_appends_a_row(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["add_item_requested"]("Nouvelle tâche")

    assert [row.label for row in view.rows] == ["Nouvelle tâche"]


def test_add_item_requested_with_empty_label_reports_an_error(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["add_item_requested"]("   ")

    assert view.last_error is not None
    assert view.rows == ()


def test_item_state_changed_updates_the_row_state(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["item_state_changed"](item.id_todo_item, TodoStateEnum.E_DONE)

    assert view.rows[0].state is TodoStateEnum.E_DONE


def test_delete_then_undo_restores_the_item(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["item_delete_clicked"](item.id_todo_item)

    assert view.rows == ()
    assert view.deleted_toast_label == "Ecrire le brief"

    view.callbacks["undo_delete_clicked"]()

    assert [row.label for row in view.rows] == ["Ecrire le brief"]


def test_undo_without_a_prior_delete_is_a_no_op(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["undo_delete_clicked"]()

    assert view.rows == ()
    assert view.last_error is None


def test_delete_list_clicked_removes_every_row(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    service.add_item("pom-1", "Item A")
    service.add_item("pom-1", "Item B")
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["delete_list_clicked"]()

    assert view.rows == ()


def test_duplicate_clicked_adds_a_second_row(config_repository: FakeConfigRepository) -> None:
    view = FakeTodoListView()
    service = TodoService(config_repository)
    service.add_item("pom-1", "Ecrire le brief")
    item = service.list_for_pomodoro("pom-1")[0]
    presenter = TodoListPresenter(view, service)
    presenter.show_for_pomodoro("pom-1")

    view.callbacks["item_duplicate_clicked"](item.id_todo_item)

    assert len(view.rows) == 2


# EOF
