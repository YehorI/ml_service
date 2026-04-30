from datetime import datetime

from database_repository.dto.users import User
from database_repository.models import MLTaskORM, UserORM, UserRoleORM
from database_repository.models.task import TaskStatusORM
from loguru import logger
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_common.messaging.schemas import (BillingRequestMessage,
                                                 PredictRequestMessage)
from ml_service_common.sqlalchemy_alt.service import SQLAlchemyService
from ml_service_wallet.database.repositories import (
    SqlAlchemyAltBalanceRepository, SqlAlchemyAltTransactionRepository)
from ml_service_wallet.services.wallet_service import (InsufficientFundsError,
                                                       WalletService)
from sqlalchemy import select


class BillingMessageHandler:
    def __init__(self, db: SQLAlchemyService, publisher: RabbitMQPublisher) -> None:
        self._db = db
        self._publisher = publisher

    async def handle(self, body: bytes) -> None:
        message = BillingRequestMessage.model_validate_json(body)
        logger.info(f"Billing task_id={message.task_id} user_id={message.user_id} amount={message.cost_per_request}")
        async with self._db.transaction():
            user_orm = (
                await self._db.session.execute(select(UserORM).where(UserORM.id == message.user_id))
            ).scalar_one_or_none()
            if user_orm is None:
                logger.error(f"User id={message.user_id} not found, failing task_id={message.task_id}")
                await self._fail_task(message.task_id)
                return

            user = _to_user(user_orm)
            balance_repo = SqlAlchemyAltBalanceRepository(self._db)
            txn_repo = SqlAlchemyAltTransactionRepository(self._db)
            wallet = await balance_repo.get_by_user_id(user.user_id)
            if wallet is None:
                logger.warning(f"Wallet not found for user_id={message.user_id}, failing task_id={message.task_id}")
                await self._fail_task(message.task_id)
                return

            try:
                wallet_service = WalletService(balance_repo, txn_repo)
                await wallet_service.charge_for_task(
                    user=user,
                    wallet=wallet,
                    task_id=message.task_id,
                    amount=message.cost_per_request,
                )
            except InsufficientFundsError as exc:
                logger.warning(f"Billing failed task_id={message.task_id}: {exc}")
                await self._fail_task(message.task_id)
                return

        predict_message = PredictRequestMessage(
            task_id=message.task_id,
            model_id=message.model_id,
            model_name=message.model_name,
            input_data=message.input_data,
        )
        await self._publisher.publish(predict_message)
        logger.info(f"Billing succeeded, enqueued prediction for task_id={message.task_id}")

    async def _fail_task(self, task_id: int) -> None:
        orm = (
            await self._db.session.execute(select(MLTaskORM).where(MLTaskORM.id == task_id))
        ).scalar_one_or_none()
        if orm is not None:
            orm.status = TaskStatusORM.FAILED
            orm.completed_at = datetime.utcnow()


def _to_user(orm: UserORM) -> User:
    from database_repository.dto.users import AdminUser, UserRole
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
