from unittest.mock import AsyncMock

from ml_service_users.domains.user import User
from ml_service_wallet.domains.transaction import DepositTransaction
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.services.wallet_service import WalletService


def _user() -> User:
    return User(user_id=1, username="alice", email="alice@example.com", password_hash="x")


class TestRefundForTask:
    async def test_refund_increases_balance(self) -> None:
        user = _user()
        wallet = Wallet(user_id=1, amount=10.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()
        tx_repo.save.side_effect = lambda tx: tx

        service = WalletService(balance_repo, tx_repo)
        tx = await service.refund_for_task(user, wallet, task_id=99, amount=5.0)

        assert isinstance(tx, DepositTransaction)
        assert tx.is_applied is True
        assert tx.ml_task_id == 99
        assert wallet.amount == 15.0
        balance_repo.update.assert_called_once_with(wallet)
        tx_repo.save.assert_called_once()

    async def test_refund_persists_task_link(self) -> None:
        user = _user()
        wallet = Wallet(user_id=1, amount=0.0)
        balance_repo = AsyncMock()
        tx_repo = AsyncMock()
        tx_repo.save.side_effect = lambda tx: tx

        service = WalletService(balance_repo, tx_repo)
        await service.refund_for_task(user, wallet, task_id=42, amount=1.5)

        saved = tx_repo.save.call_args[0][0]
        assert isinstance(saved, DepositTransaction)
        assert saved.ml_task_id == 42
        assert saved.amount == 1.5
        assert saved.transaction_type.value == "deposit"
