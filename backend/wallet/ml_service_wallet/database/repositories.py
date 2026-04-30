from database_repository.dto.users import AdminUser, User, UserRole
from database_repository.models import (TransactionORM, TransactionTypeORM,
                                        UserORM, UserRoleORM, WalletORM)
from ml_service_wallet.database.service import Service
from ml_service_wallet.domains.transaction import (DebitTransaction,
                                                   DepositTransaction,
                                                   Transaction)
from ml_service_wallet.domains.wallet import Wallet
from ml_service_wallet.interfaces.repositories import (BalanceRepository,
                                                       TransactionRepository)
from sqlalchemy import select


def to_domain_user(orm: UserORM) -> User:
    if orm.role == UserRoleORM.ADMIN:
        return AdminUser(
            user_id=orm.id,
            username=orm.username,
            email=orm.email,
            password_hash=orm.password_hash,
            created_at=orm.created_at,
        )
    return User(
        user_id=orm.id,
        username=orm.username,
        email=orm.email,
        password_hash=orm.password_hash,
        role=UserRole.USER,
        created_at=orm.created_at,
    )


def to_domain_wallet(orm: WalletORM) -> Wallet:
    return Wallet(user_id=orm.user_id, amount=float(orm.amount))


def to_domain_transaction(orm: TransactionORM, user: User, wallet: Wallet) -> Transaction:
    if orm.transaction_type == TransactionTypeORM.DEPOSIT:
        tx = DepositTransaction(
            transaction_id=orm.id,
            user=user,
            wallet=wallet,
            amount=float(orm.amount),
            created_at=orm.created_at,
        )
    else:
        tx = DebitTransaction(
            transaction_id=orm.id,
            user=user,
            wallet=wallet,
            amount=float(orm.amount),
            ml_task_id=int(orm.ml_task_id or 0),
            created_at=orm.created_at,
        )
    if orm.is_applied:
        tx._is_applied = True
    return tx


class SqlAlchemyAltBalanceRepository(BalanceRepository):
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


class SqlAlchemyAltTransactionRepository(TransactionRepository):
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
