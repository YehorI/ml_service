from database_repository.models import (
    MLModelORM,
    MLTaskORM,
    PredictionResultORM,
    TransactionORM,
    TransactionTypeORM,
    UserORM,
    UserRoleORM,
    WalletORM,
)
from ml_service_model.domains.task import MLTask, PredictionResult, TaskStatus
from ml_service_users.domains.user import AdminUser, User, UserRole
from ml_service_wallet.domains.transaction import DebitTransaction, DepositTransaction, Transaction
from ml_service_wallet.domains.wallet import Wallet


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


class _PseudoModel:
    def __init__(self, orm: MLModelORM) -> None:
        self._orm = orm

    @property
    def model_id(self) -> int:
        return self._orm.id

    @property
    def name(self) -> str:
        return self._orm.name

    @property
    def description(self) -> str:
        return self._orm.description

    @property
    def cost_per_request(self) -> float:
        return float(self._orm.cost_per_request)

    @property
    def is_active(self) -> bool:
        return bool(self._orm.is_active)


def to_domain_task(orm: MLTaskORM, user: User, model_orm: MLModelORM) -> MLTask:
    task = MLTask(
        task_id=orm.id,
        user=user,
        model=_PseudoModel(model_orm),
        input_data=orm.input_data,
        created_at=orm.created_at,
    )
    task._status = TaskStatus(orm.status.value)
    task._completed_at = orm.completed_at
    return task


def to_domain_prediction_result(orm: PredictionResultORM) -> PredictionResult:
    return PredictionResult(
        result_id=orm.id,
        task_id=orm.task_id,
        output_data=orm.output_data,
        credits_charged=float(orm.credits_charged),
        created_at=orm.created_at,
    )

