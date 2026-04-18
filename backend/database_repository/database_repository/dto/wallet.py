from dataclasses import dataclass, field


@dataclass
class WalletCreateDTO:
    user_id: int
    amount: float = field(default=0.0)


@dataclass
class WalletReadDTO:
    id: int
    user_id: int
    amount: float
