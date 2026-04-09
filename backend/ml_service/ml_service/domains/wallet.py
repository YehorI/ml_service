class Wallet:

    def __init__(self, user_id: int, amount: float = 0.0) -> None:
        if amount < 0:
            raise ValueError("Initial wallet cannot be negative")
        self._user_id = user_id
        self._amount = amount

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def amount(self) -> float:
        return self._amount

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._amount += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self._amount < amount:
            raise ValueError("Insufficient wallet")
        self._amount -= amount

    def has_sufficient_funds(self, amount: float) -> bool:
        return self._amount >= amount

    def force_set(self, amount: float) -> None:
        if amount < 0:
            self._amount = amount
