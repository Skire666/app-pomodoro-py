"""Collection of TODO items, spanning every pomodoro."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.models.todo_item_model import TodoItemModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.todo_state_enum import TodoStateEnum
from pomodoro.shared.validation_result import ValidationResult


class TodoCollectionModel:
    """An ordered collection of `TodoItemModel` instances.

    Items from every pomodoro are stored together; callers scope the
    collection to a single pomodoro through `for_pomodoro`.
    """

    def __init__(self, items: list[TodoItemModel], created_at: datetime, modified_at: datetime) -> None:
        """Initialize the collection from its already-resolved fields."""
        self._items = items
        self._created_at = created_at
        self._modified_at = modified_at

    def __iter__(self) -> Iterator[TodoItemModel]:
        """Iterate over the TODO items held by this collection."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of TODO items held by this collection."""
        return len(self._items)

    def __getitem__(self, index: int) -> TodoItemModel:
        """Return the TODO item stored at `index`."""
        return self._items[index]

    @property
    def items(self) -> tuple[TodoItemModel, ...]:
        """All TODO items currently held by this collection, in storage order."""
        return tuple(self._items)

    @items.setter
    def items(self, value: list[TodoItemModel]) -> None:
        """Replace the entire contents of this collection."""
        self._items = value

    @property
    def created_at(self) -> datetime:
        """Timestamp at which this collection was created."""
        return self._created_at

    @property
    def modified_at(self) -> datetime:
        """Timestamp at which this collection was last modified."""
        return self._modified_at

    def create(self, item: TodoItemModel) -> None:
        """Append a new TODO item to the collection."""
        self._items.append(item)

    def read(self, id_todo_item: str) -> TodoItemModel | None:
        """Return the TODO item matching `id_todo_item`, or None if absent."""
        for item in self._items:
            if item.id_todo_item == id_todo_item:
                return item
        return None

    def update(self, item: TodoItemModel) -> bool:
        """Replace the stored TODO item sharing `item`'s id.

        Args:
            item: The new value to store in place of the matching entry.

        Returns:
            True if a matching entry was found and replaced, False otherwise.
        """
        for index, existing in enumerate(self._items):
            if existing.id_todo_item == item.id_todo_item:
                self._items[index] = item
                return True
        return False

    def delete(self, id_todo_item: str) -> bool:
        """Remove the TODO item matching `id_todo_item`.

        Returns:
            True if a matching entry was found and removed, False otherwise.
        """
        item = self.read(id_todo_item)
        if item is None:
            return False
        self._items.remove(item)
        return True

    def delete_many(self, ids: Iterable[str]) -> int:
        """Remove every TODO item whose id is in `ids`.

        Args:
            ids: Identifiers of the TODO items to remove.

        Returns:
            The number of entries actually removed.
        """
        id_set = set(ids)
        before = len(self._items)
        self._items = [item for item in self._items if item.id_todo_item not in id_set]
        return before - len(self._items)

    def for_pomodoro(self, id_pomodoro: str) -> tuple[TodoItemModel, ...]:
        """Return every TODO item belonging to `id_pomodoro`, in storage order."""
        return tuple(item for item in self._items if item.id_pomodoro == id_pomodoro)

    def count_active_for_pomodoro(self, id_pomodoro: str) -> int:
        """Count non-cancelled TODO items for `id_pomodoro` (spec §2.2 tab label)."""
        return sum(
            1
            for item in self._items
            if item.id_pomodoro == id_pomodoro and item.state is not TodoStateEnum.E_CANCELLED
        )

    def delete_for_pomodoro(self, id_pomodoro: str) -> int:
        """Remove every TODO item belonging to `id_pomodoro`.

        Returns:
            The number of entries actually removed.
        """
        before = len(self._items)
        self._items = [item for item in self._items if item.id_pomodoro != id_pomodoro]
        return before - len(self._items)

    def serialize(self) -> dict[str, Any]:
        """Serialize this collection to a JSON-compatible dictionary."""
        return {
            "items": [item.to_dict() for item in self._items],
            "created_at": self._created_at.isoformat(),
            "modified_at": self._modified_at.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        """Rebuild a collection from a dictionary produced by `serialize`.

        Args:
            data: A JSON-compatible dictionary as returned by `serialize`.

        Returns:
            The hydrated collection.
        """
        return cls(
            items=[TodoItemModel.from_dict(raw) for raw in data["items"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
        )

    @classmethod
    def get_default(cls) -> Self:
        """Build an empty collection stamped with the current time."""
        now = datetime.now(UTC)
        return cls(items=[], created_at=now, modified_at=now)

    def mark_as_created(self) -> None:
        """Stamp `created_at` and `modified_at` with the current time."""
        now = datetime.now(UTC)
        self._created_at = now
        self._modified_at = now

    def mark_as_modified(self) -> None:
        """Stamp `modified_at` with the current time."""
        self._modified_at = datetime.now(UTC)

    def validate(self, context: object | None = None) -> ValidationResult:
        """Validate every TODO item held by this collection.

        Args:
            context: Forwarded unchanged to each item's own `validate`.

        Returns:
            The first failing item's ValidationResult, or a success result
            if every item is valid.
        """
        for item in self._items:
            result = item.validate(context)
            if not result.is_valid:
                return result
        return ValidationResult.ok()

    def copy(self, mode: CopyModeEnum) -> Self:
        """Copy this collection and every TODO item it holds.

        Args:
            mode: Forwarded to each item's own `copy`.

        Returns:
            The copied collection.
        """
        cloned_items = [item.copy(mode) for item in self._items]
        if mode is CopyModeEnum.E_BUSINESS:
            now = datetime.now(UTC)
            return type(self)(items=cloned_items, created_at=now, modified_at=now)
        return type(self)(items=cloned_items, created_at=self._created_at, modified_at=self._modified_at)

    def clear(self) -> None:
        """Reset this collection to an empty, default state, in place."""
        default = self.get_default()
        self._items = list(default.items)
        self._created_at = default.created_at
        self._modified_at = default.modified_at


# EOF
