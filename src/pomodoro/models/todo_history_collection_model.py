"""Collection of TODO item state-change history entries."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.models.todo_history_entry_model import TodoHistoryEntryModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.validation_result import ValidationResult


class TodoHistoryCollectionModel:
    """An ordered collection of `TodoHistoryEntryModel` instances."""

    def __init__(self, items: list[TodoHistoryEntryModel], created_at: datetime, modified_at: datetime) -> None:
        """Initialize the collection from its already-resolved fields."""
        self._items = items
        self._created_at = created_at
        self._modified_at = modified_at

    def __iter__(self) -> Iterator[TodoHistoryEntryModel]:
        """Iterate over the history entries held by this collection."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of history entries held by this collection."""
        return len(self._items)

    def __getitem__(self, index: int) -> TodoHistoryEntryModel:
        """Return the history entry stored at `index`."""
        return self._items[index]

    @property
    def items(self) -> tuple[TodoHistoryEntryModel, ...]:
        """All history entries currently held by this collection, in storage order."""
        return tuple(self._items)

    @items.setter
    def items(self, value: list[TodoHistoryEntryModel]) -> None:
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

    def create(self, item: TodoHistoryEntryModel) -> None:
        """Append a new history entry to the collection."""
        self._items.append(item)

    def read(self, id_history_entry: str) -> TodoHistoryEntryModel | None:
        """Return the history entry matching `id_history_entry`, or None if absent."""
        for item in self._items:
            if item.id_history_entry == id_history_entry:
                return item
        return None

    def delete_many(self, ids: Iterable[str]) -> int:
        """Remove every history entry whose id is in `ids`.

        Args:
            ids: Identifiers of the history entries to remove.

        Returns:
            The number of entries actually removed.
        """
        id_set = set(ids)
        before = len(self._items)
        self._items = [item for item in self._items if item.id_history_entry not in id_set]
        return before - len(self._items)

    def purge(self, max_entries: int) -> int:
        """Drop the oldest entries beyond `max_entries` (FIFO, spec §2.6).

        Args:
            max_entries: The maximum number of entries to keep.

        Returns:
            The number of entries actually removed.
        """
        if len(self._items) <= max_entries:
            return 0
        ordered = sorted(self._items, key=lambda item: item.changed_at)
        overflow = len(ordered) - max_entries
        ids_to_remove = [item.id_history_entry for item in ordered[:overflow]]
        return self.delete_many(ids_to_remove)

    def search(self, *, most_recent_first: bool = True) -> tuple[TodoHistoryEntryModel, ...]:
        """Return every entry sorted by change date (spec §2.6 default sort).

        Args:
            most_recent_first: If True (the default), sort descending.

        Returns:
            The sorted history entries.
        """
        return tuple(sorted(self._items, key=lambda item: item.changed_at, reverse=most_recent_first))

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
            items=[TodoHistoryEntryModel.from_dict(raw) for raw in data["items"]],
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
        """Validate every history entry held by this collection.

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
        """Copy this collection and every history entry it holds.

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
