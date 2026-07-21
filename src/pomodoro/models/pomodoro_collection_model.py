"""Collection of pomodoro definitions."""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from typing import Any, Self

from pomodoro.models.pomodoro_model import PomodoroModel
from pomodoro.shared.enums.copy_mode_enum import CopyModeEnum
from pomodoro.shared.enums.pomodoro_sort_mode_enum import PomodoroSortModeEnum
from pomodoro.shared.validation_result import ValidationResult


class PomodoroCollectionModel:
    """An ordered collection of `PomodoroModel` instances."""

    def __init__(self, items: list[PomodoroModel], created_at: datetime, modified_at: datetime) -> None:
        """Initialize the collection from its already-resolved fields."""
        self._items = items
        self._created_at = created_at
        self._modified_at = modified_at

    def __iter__(self) -> Iterator[PomodoroModel]:
        """Iterate over the pomodoros held by this collection."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of pomodoros held by this collection."""
        return len(self._items)

    def __getitem__(self, index: int) -> PomodoroModel:
        """Return the pomodoro stored at `index`."""
        return self._items[index]

    @property
    def items(self) -> tuple[PomodoroModel, ...]:
        """All pomodoros currently held by this collection, in storage order."""
        return tuple(self._items)

    @items.setter
    def items(self, value: list[PomodoroModel]) -> None:
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

    def create(self, item: PomodoroModel) -> None:
        """Append a new pomodoro to the collection."""
        self._items.append(item)

    def read(self, id_pomodoro: str) -> PomodoroModel | None:
        """Return the pomodoro matching `id_pomodoro`, or None if absent."""
        for item in self._items:
            if item.id_pomodoro == id_pomodoro:
                return item
        return None

    def update(self, item: PomodoroModel) -> bool:
        """Replace the stored pomodoro sharing `item`'s id.

        Args:
            item: The new value to store in place of the matching entry.

        Returns:
            True if a matching entry was found and replaced, False otherwise.
        """
        for index, existing in enumerate(self._items):
            if existing.id_pomodoro == item.id_pomodoro:
                self._items[index] = item
                return True
        return False

    def delete(self, id_pomodoro: str) -> bool:
        """Remove the pomodoro matching `id_pomodoro`.

        Returns:
            True if a matching entry was found and removed, False otherwise.
        """
        item = self.read(id_pomodoro)
        if item is None:
            return False
        self._items.remove(item)
        return True

    def delete_many(self, ids: Iterable[str]) -> int:
        """Remove every pomodoro whose id is in `ids`.

        Args:
            ids: Identifiers of the pomodoros to remove.

        Returns:
            The number of entries actually removed.
        """
        id_set = set(ids)
        before = len(self._items)
        self._items = [item for item in self._items if item.id_pomodoro not in id_set]
        return before - len(self._items)

    def search(
        self,
        name_filter: str = "",
        sort_mode: PomodoroSortModeEnum = PomodoroSortModeEnum.E_UNSET,
    ) -> tuple[PomodoroModel, ...]:
        """Filter and sort pomodoros per the list screen rules (spec §2.1).

        Args:
            name_filter: Case-insensitive substring to match against names.
            sort_mode: The sort criterion to apply; defaults to alphabetical order.

        Returns:
            The filtered and sorted pomodoros.
        """
        results = list(self._items)
        if name_filter:
            needle = name_filter.casefold()
            results = [item for item in results if needle in item.name.casefold()]
        return tuple(self._sort(results, sort_mode))

    def _sort(self, items: list[PomodoroModel], sort_mode: PomodoroSortModeEnum) -> list[PomodoroModel]:
        """Sort `items` according to `sort_mode`."""
        if sort_mode is PomodoroSortModeEnum.E_DURATION:
            return sorted(items, key=lambda item: item.duration_seconds)
        if sort_mode is PomodoroSortModeEnum.E_LAST_USED:
            return sorted(items, key=self._last_used_sort_key, reverse=True)
        return sorted(items, key=lambda item: item.name.casefold())

    @staticmethod
    def _last_used_sort_key(item: PomodoroModel) -> tuple[bool, datetime]:
        """Sort key placing recently used items first, unused items last."""
        used_at = item.last_used_at
        return (used_at is not None, used_at or datetime.min.replace(tzinfo=UTC))

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
            items=[PomodoroModel.from_dict(raw) for raw in data["items"]],
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
        """Validate every pomodoro held by this collection.

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
        """Copy this collection and every pomodoro it holds.

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
