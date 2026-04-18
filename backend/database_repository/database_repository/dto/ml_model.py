from dataclasses import dataclass, field


@dataclass
class MLModelCreateDTO:
    name: str
    description: str
    cost_per_request: float
    is_active: bool = field(default=True)


@dataclass
class MLModelReadDTO:
    id: int
    name: str
    description: str
    cost_per_request: float
    is_active: bool
