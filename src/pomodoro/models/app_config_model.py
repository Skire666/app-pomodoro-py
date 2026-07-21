"""Singleton aggregate root of `config-pomodoro.json` (see AGENTS.md §10)."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from datetime import UTC, datetime
from typing import Any, ClassVar, Final, Self

from pomodoro.models.active_session_model import ActiveSessionModel
from pomodoro.models.pomodoro_collection_model import PomodoroCollectionModel
from pomodoro.models.pomodoro_history_collection_model import PomodoroHistoryCollectionModel
from pomodoro.models.todo_collection_model import TodoCollectionModel
from pomodoro.models.todo_history_collection_model import TodoHistoryCollectionModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.validation_result import ValidationResult

SINGLETON_ID: Final[str] = "APP_CONFIG"
MAX_POMODORO_HISTORY_ENTRIES: Final[int] = 20
MAX_TODO_HISTORY_ENTRIES: Final[int] = 100


class AppConfigModel:
    """Aggregate root of `config-pomodoro.json`: every persisted collection.

    Exposed as a process-wide singleton (AGENTS.md §10): the single
    tolerated exception to the dependency-injection rule of §9, because
    configuration must be readable from anywhere. It remains read-mostly;
    only `ConfigRepository` writes it back to disk.
    """

    _instance: ClassVar[AppConfigModel | None] = None

    def __init__(
        self,
        pomodoros: PomodoroCollectionModel,
        todos: TodoCollectionModel,
        pomodoro_history: PomodoroHistoryCollectionModel,
        todo_history: TodoHistoryCollectionModel,
        active_session: ActiveSessionModel | None,
        created_at: datetime,
        modified_at: datetime,
    ) -> None:
        """Initialize the aggregate from its already-resolved collections."""
        self._pomodoros = pomodoros
        self._todos = todos
        self._pomodoro_history = pomodoro_history
        self._todo_history = todo_history
        self._active_session = active_session
        self._created_at = created_at
        self._modified_at = modified_at

    @classmethod
    def instance(cls) -> AppConfigModel:
        """Return the process-wide singleton, creating a default one lazily."""
        if cls._instance is None:
            cls._instance = cls.get_default()
        return cls._instance

    @classmethod
    def set_instance(cls, config: AppConfigModel) -> None:
        """Replace the process-wide singleton.

        Called once, at startup, by `ConfigRepository` after loading the
        configuration file from disk.

        Args:
            config: The freshly hydrated configuration to publish globally.
        """
        cls._instance = config

    @property
    def id_app_config(self) -> str:
        """Constant identifier of the singleton configuration aggregate."""
        return SINGLETON_ID

    @property
    def pomodoros(self) -> PomodoroCollectionModel:
        """The collection of pomodoro definitions."""
        return self._pomodoros

    @pomodoros.setter
    def pomodoros(self, value: PomodoroCollectionModel) -> None:
        """Replace the collection of pomodoro definitions."""
        self._pomodoros = value

    @property
    def todos(self) -> TodoCollectionModel:
        """The collection of TODO items, across every pomodoro."""
        return self._todos

    @todos.setter
    def todos(self, value: TodoCollectionModel) -> None:
        """Replace the collection of TODO items."""
        self._todos = value

    @property
    def pomodoro_history(self) -> PomodoroHistoryCollectionModel:
        """The collection of pomodoro session history entries."""
        return self._pomodoro_history

    @pomodoro_history.setter
    def pomodoro_history(self, value: PomodoroHistoryCollectionModel) -> None:
        """Replace the collection of pomodoro session history entries."""
        self._pomodoro_history = value

    @property
    def todo_history(self) -> TodoHistoryCollectionModel:
        """The collection of TODO state-change history entries."""
        return self._todo_history

    @todo_history.setter
    def todo_history(self, value: TodoHistoryCollectionModel) -> None:
        """Replace the collection of TODO state-change history entries."""
        self._todo_history = value

    @property
    def active_session(self) -> ActiveSessionModel | None:
        """The currently running pomodoro session, or None if idle (spec §2.4)."""
        return self._active_session

    @active_session.setter
    def active_session(self, value: ActiveSessionModel | None) -> None:
        """Replace the currently running pomodoro session."""
        self._active_session = value

    @property
    def created_at(self) -> datetime:
        """Timestamp at which the configuration file was first created."""
        return self._created_at

    @property
    def modified_at(self) -> datetime:
        """Timestamp at which the configuration file was last modified."""
        return self._modified_at

    @property
    def fieldnames(self) -> tuple[str, ...]:
        """Names of every persisted field, in declaration order."""
        return (
            "pomodoros",
            "todos",
            "pomodoro_history",
            "todo_history",
            "active_session",
            "created_at",
            "modified_at",
        )

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate every collection held by this aggregate.

        Args:
            context: Forwarded unchanged to each collection's own `validate`.

        Returns:
            The first failing collection's ValidationResult, or a success
            result if every collection is valid.
        """
        collections = (self._pomodoros, self._todos, self._pomodoro_history, self._todo_history)
        for collection in collections:
            result = collection.validate(context)
            if not result.is_valid:
                return result
        return ValidationResult.ok()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this aggregate to a JSON-compatible dictionary."""
        return {
            "pomodoros": self._pomodoros.serialize(),
            "todos": self._todos.serialize(),
            "pomodoro_history": self._pomodoro_history.serialize(),
            "todo_history": self._todo_history.serialize(),
            "active_session": self._active_session.to_dict() if self._active_session is not None else None,
            "created_at": self._created_at.isoformat(),
            "modified_at": self._modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Rebuild the aggregate from a dictionary produced by `to_dict`.

        Args:
            data: A JSON-compatible dictionary as returned by `to_dict`.

        Returns:
            The hydrated aggregate.
        """
        active_session_raw = data.get("active_session")
        return cls(
            pomodoros=PomodoroCollectionModel.deserialize(data["pomodoros"]),
            todos=TodoCollectionModel.deserialize(data["todos"]),
            pomodoro_history=PomodoroHistoryCollectionModel.deserialize(data["pomodoro_history"]),
            todo_history=TodoHistoryCollectionModel.deserialize(data["todo_history"]),
            active_session=ActiveSessionModel.from_dict(active_session_raw) if active_session_raw else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build an empty aggregate stamped with the current time."""
        now = datetime.now(UTC)
        return cls(
            pomodoros=PomodoroCollectionModel.get_default(),
            todos=TodoCollectionModel.get_default(),
            pomodoro_history=PomodoroHistoryCollectionModel.get_default(),
            todo_history=TodoHistoryCollectionModel.get_default(),
            active_session=None,
            created_at=now,
            modified_at=now,
        )

    def mark_as_created(self) -> None:
        """Stamp `created_at` and `modified_at` with the current time."""
        now = datetime.now(UTC)
        self._created_at = now
        self._modified_at = now

    def mark_as_modified(self) -> None:
        """Stamp `modified_at` with the current time."""
        self._modified_at = datetime.now(UTC)

    def copy(self, mode: CopyModeEnum) -> Self:
        """Copy this aggregate and every collection it holds.

        Args:
            mode: Forwarded to each collection's own `copy`.

        Returns:
            The copied aggregate.
        """
        cloned_pomodoros = self._pomodoros.copy(mode)
        cloned_todos = self._todos.copy(mode)
        cloned_pomodoro_history = self._pomodoro_history.copy(mode)
        cloned_todo_history = self._todo_history.copy(mode)
        cloned_active_session = self._active_session.copy(mode) if self._active_session is not None else None
        timestamps = (
            (datetime.now(UTC),) * 2 if mode is CopyModeEnum.E_BUSINESS else (self._created_at, self._modified_at)
        )
        return type(self)(
            pomodoros=cloned_pomodoros,
            todos=cloned_todos,
            pomodoro_history=cloned_pomodoro_history,
            todo_history=cloned_todo_history,
            active_session=cloned_active_session,
            created_at=timestamps[0],
            modified_at=timestamps[1],
        )

    def clear(self) -> None:
        """Reset every collection to an empty, default state, in place."""
        default = self.get_default()
        self._pomodoros = default.pomodoros
        self._todos = default.todos
        self._pomodoro_history = default.pomodoro_history
        self._todo_history = default.todo_history
        self._active_session = default.active_session
        self._created_at = default.created_at
        self._modified_at = default.modified_at


# EOF
