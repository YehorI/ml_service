from dataclasses import dataclass, field
from typing import Any


@dataclass
class FixtureItem:
    model: str
    fields: dict[str, Any] = field(default_factory=dict)
