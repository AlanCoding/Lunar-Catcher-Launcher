"""Mass bookkeeping only; no component sizing or assumed component masses."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from collections.abc import Iterable


class MassCategory(str, Enum):
    PERMANENT_IMPORTED = "permanent_imported"
    PERMANENT_LOCAL = "permanent_local"
    EXPENDABLE_LOCAL_PER_LAUNCH = "expendable_local_per_launch"
    PAYLOAD = "payload"


@dataclass(frozen=True)
class MassItem:
    """One total component-category mass [kg]; split mixed-origin assemblies.

    None denotes unsized mass. Unresolved masses must not vanish from totals.
    Payload mass means useful mass successfully captured, excluding climbers.
    """

    name: str
    category: MassCategory
    mass_kg: float | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("A mass item needs a name")
        if not isinstance(self.category, MassCategory):
            raise ValueError("Use an explicit MassCategory")
        if self.mass_kg is not None and (
            not isfinite(self.mass_kg) or self.mass_kg < 0
        ):
            raise ValueError("Mass must be finite and nonnegative, or None")


def category_total_kg(items: Iterable[MassItem], category: MassCategory) -> float:
    """Return category total [kg]; raise if a listed item is unsized."""
    selected = [item for item in items if item.category == category]
    unknown = [item.name for item in selected if item.mass_kg is None]
    if unknown:
        raise ValueError(f"Unsized mass items: {', '.join(unknown)}")
    return sum(item.mass_kg for item in selected)


def imported_mass_ratio(items: Iterable[MassItem]) -> float:
    """Imported permanent kg / useful captured kg; completeness is caller's duty.

    This cannot certify that every required BOM item has been listed. A complete
    reviewed BOM and physics feasibility checks remain mandatory before use.
    """
    entries = tuple(items)
    imported = category_total_kg(entries, MassCategory.PERMANENT_IMPORTED)
    payload = category_total_kg(entries, MassCategory.PAYLOAD)
    if payload <= 0:
        raise ValueError("Successfully captured payload mass must be positive")
    return imported / payload
