from ml_service_common.sqlalchemy.service import Service
from sqlalchemy import select

from database_repository.models import TransactionORM, TransactionTypeORM, UserORM, WalletORM
from database_repository.repositories._mappers import (
    to_domain_transaction,
    to_domain_user,
    to_domain_wallet,
)
from wallet.domains.transaction import DebitTransaction, DepositTransaction, Transaction
from wallet.domains.wallet import Wallet
from wallet.interfaces.repositories import BalanceRepository, TransactionRepository


class SqlAlchemyBalanceRepository(BalanceRepository):
    def __init__(self, service: Service) -> None:
        self._service = service

    async def get_by_user_id(self, user_id: int) -> Wallet | None:
        row = (
            await self._service.session.execute(select(WalletORM).where(WalletORM.user_id == user_id))
        ).scalar_one_or_none()
        return None if row is None else to_domain_wallet(row)

    async def save(self, wallet: Wallet) -> Wallet:
        orm = WalletORM(user_id=wallet.user_id, amount=wallet.amount)
        self._service.session.add(orm)
        await self._service.session.flush()
        return to_domain_wallet(orm)

    async def update(self, wallet: Wallet) -> Wallet:
        orm = (
            await self._service.session.execute(select(WalletORM).where(WalletORM.user_id == wallet.user_id))
        ).scalar_one()
        orm.amount = wallet.amount
        return to_domain_wallet(orm)


class SqlAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, service: Service) -> None:
        self._service = service

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        tx = (
            await self._service.session.execute(select(TransactionORM).where(TransactionORM.id == transaction_id))
        ).scalar_one_or_none()
        if tx is None:
            return None
        user_orm = (await self._service.session.execute(select(UserORM).where(UserORM.id == tx.user_id))).scalar_one()
        wallet_orm = (
            await self._service.session.execute(select(WalletORM).where(WalletORM.id == tx.wallet_id))
        ).scalar_one()
        return to_domain_transaction(tx, to_domain_user(user_orm), to_domain_wallet(wallet_orm))

    async def list_by_user(self, user_id: int) -> list[Transaction]:
        user_orm = (await self._service.session.execute(select(UserORM).where(UserORM.id == user_id))).scalar_one()
        wallet_orm = (
            await self._service.session.execute(select(WalletORM).where(WalletORM.user_id == user_id))
        ).scalar_one()
        txs = (
            await self._service.session.execute(
                select(TransactionORM).where(TransactionORM.user_id == user_id).order_by(TransactionORM.created_at)
            )
        ).scalars().all()
        user = to_domain_user(user_orm)
        wallet = to_domain_wallet(wallet_orm)
        return [to_domain_transaction(t, user, wallet) for t in txs]

    async def list_all(self) -> list[Transaction]:
        txs = (await self._service.session.execute(select(TransactionORM).order_by(TransactionORM.created_at))).scalars().all()
        result: list[Transaction] = []
        for tx in txs:
            user_orm = (
                await self._service.session.execute(select(UserORM).where(UserORM.id == tx.user_id))
            ).scalar_one()
            wallet_orm = (
                await self._service.session.execute(select(WalletORM).where(WalletORM.id == tx.wallet_id))
            ).scalar_one()
            result.append(to_domain_transaction(tx, to_domain_user(user_orm), to_domain_wallet(wallet_orm)))
        return result

    async def save(self, transaction: Transaction) -> Transaction:
        tx_type = (
            TransactionTypeORM.DEPOSIT
            if isinstance(transaction, DepositTransaction)
            else TransactionTypeORM.DEBIT
        )
        wallet_orm = (
            await self._service.session.execute(select(WalletORM).where(WalletORM.user_id == transaction.user.user_id))
        ).scalar_one()
        orm = TransactionORM(
            user_id=transaction.user.user_id,
            wallet_id=wallet_orm.id,
            amount=transaction.amount,
            transaction_type=tx_type,
            ml_task_id=getattr(transaction, "ml_task_id", None),
            created_at=transaction.created_at,
            is_applied=transaction.is_applied,
        )
        self._service.session.add(orm)
        await self._service.session.flush()
        return await self.get_by_id(int(orm.id))

