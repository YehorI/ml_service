from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from users.domains.user import User
from users.services.user_service import (
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)
from wallet.domains.transaction import DebitTransaction, DepositTransaction
from wallet.domains.wallet import Wallet
from wallet.services.wallet_service import InsufficientFundsError, WalletService


def _make_user(user_id: int = 1, username: str = "alice", password_hash: str = "hash123") -> User:
    return User(
        user_id=user_id,
        username=username,
        email=f"{username}@example.com",
        password_hash=password_hash,
    )


def _make_wallet(user_id: int = 1, amount: float = 100.0) -> Wallet:
    return Wallet(user_id=user_id, amount=amount)


class TestUserServiceRegister:
    async def test_register_creates_user(self) -> None:
        repo = AsyncMock()
        repo.get_by_username.return_value = None
        repo.get_by_email.return_value = None
        repo.save.return_value = _make_user(user_id=42)

        service = UserService(user_repository=repo)
        result = await service.register("alice", "alice@example.com", "hash123")

        repo.save.assert_called_once()
        assert result.user_id == 42
        assert result.username == "alice"

    async def test_register_raises_if_username_taken(self) -> None:
        repo = AsyncMock()
        repo.get_by_username.return_value = _make_user()

        service = UserService(user_repository=repo)
        with pytest.raises(UserAlreadyExistsError):
            await service.register("alice", "new@example.com", "hash")

    async def test_register_raises_if_email_taken(self) -> None:
        repo = AsyncMock()
        repo.get_by_username.return_value = None
        repo.get_by_email.return_value = _make_user()

        service = UserService(user_repository=repo)
        with pytest.raises(UserAlreadyExistsError):
            await service.register("newuser", "alice@example.com", "hash")


class TestUserServiceAuthenticate:
    async def test_authenticate_success(self) -> None:
        user = _make_user(password_hash="correct_hash")
        repo = AsyncMock()
        repo.get_by_username.return_value = user

        service = UserService(user_repository=repo)
        result = await service.authenticate("alice", "correct_hash")

        assert result is user

    async def test_authenticate_wrong_password(self) -> None:
        user = _make_user(password_hash="correct_hash")
        repo = AsyncMock()
        repo.get_by_username.return_value = user

        service = UserService(user_repository=repo)
        with pytest.raises(InvalidPasswordError):
            await service.authenticate("alice", "wrong_hash")

    async def test_authenticate_user_not_found(self) -> None:
        repo = AsyncMock()
        repo.get_by_username.return_value = None

        service = UserService(user_repository=repo)
        with pytest.raises(UserNotFoundError):
            await service.authenticate("ghost", "any_hash")


class TestWalletServiceDeposit:
    async def test_deposit_increases_balance(self) -> None:
        user = _make_user()
        wallet = _make_wallet(amount=50.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()
        tx_repo.save.side_effect = lambda tx: tx

        service = WalletService(balance_repo, tx_repo)
        tx = await service.deposit(user, wallet, 30.0)

        assert isinstance(tx, DepositTransaction)
        assert tx.is_applied is True
        assert wallet.amount == 80.0
        balance_repo.update.assert_called_once_with(wallet)
        tx_repo.save.assert_called_once()

    async def test_deposit_saves_transaction(self) -> None:
        user = _make_user()
        wallet = _make_wallet(amount=0.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()
        tx_repo.save.side_effect = lambda tx: tx

        service = WalletService(balance_repo, tx_repo)
        await service.deposit(user, wallet, 100.0)

        saved_tx = tx_repo.save.call_args[0][0]
        assert saved_tx.amount == 100.0
        assert saved_tx.transaction_type.value == "deposit"


class TestWalletServiceChargeForTask:
    async def test_charge_decreases_balance(self) -> None:
        user = _make_user()
        wallet = _make_wallet(amount=100.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()
        tx_repo.save.side_effect = lambda tx: tx

        service = WalletService(balance_repo, tx_repo)
        tx = await service.charge_for_task(user, wallet, task_id=7, amount=25.0)

        assert isinstance(tx, DebitTransaction)
        assert tx.is_applied is True
        assert wallet.amount == 75.0
        assert tx.ml_task_id == 7
        balance_repo.update.assert_called_once_with(wallet)
        tx_repo.save.assert_called_once()

    async def test_charge_raises_on_insufficient_funds(self) -> None:
        user = _make_user()
        wallet = _make_wallet(amount=10.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()

        service = WalletService(balance_repo, tx_repo)
        with pytest.raises(InsufficientFundsError):
            await service.charge_for_task(user, wallet, task_id=1, amount=50.0)

        assert wallet.amount == 10.0
        balance_repo.update.assert_not_called()
        tx_repo.save.assert_not_called()

    async def test_charge_saves_transaction_with_task_reference(self) -> None:
        user = _make_user()
        wallet = _make_wallet(amount=200.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()
        tx_repo.save.side_effect = lambda tx: tx

        service = WalletService(balance_repo, tx_repo)
        await service.charge_for_task(user, wallet, task_id=42, amount=5.0)

        saved_tx = tx_repo.save.call_args[0][0]
        assert saved_tx.ml_task_id == 42
        assert saved_tx.transaction_type.value == "debit"


class TestUserTransactionHistory:
    async def test_list_by_user_returns_sorted_transactions(self) -> None:
        user = _make_user(user_id=3)
        wallet = _make_wallet(user_id=3, amount=0.0)

        tx1 = DepositTransaction(transaction_id=1, user=user, wallet=wallet, amount=100.0,
                                  created_at=datetime(2026, 1, 1))
        tx2 = DepositTransaction(transaction_id=2, user=user, wallet=wallet, amount=50.0,
                                  created_at=datetime(2026, 1, 3))
        tx3 = DepositTransaction(transaction_id=3, user=user, wallet=wallet, amount=20.0,
                                  created_at=datetime(2026, 1, 2))

        tx_repo = AsyncMock()
        tx_repo.list_by_user.return_value = [tx1, tx2, tx3]

        history = await tx_repo.list_by_user(user.user_id)
        sorted_history = sorted(history, key=lambda t: t.created_at)

        assert [t.amount for t in sorted_history] == [100.0, 20.0, 50.0]
        assert sorted_history[0].created_at < sorted_history[-1].created_at
