import pytest
from database_repository.models import (MLModelORM, MLTaskORM,
                                        PredictionResultORM, TransactionORM,
                                        TransactionTypeORM, UserORM,
                                        UserRoleORM, WalletORM)
from database_repository.models.task import TaskStatusORM
from database_repository.service import Service as DatabaseService
from sqlalchemy import func, select


async def _count(service: DatabaseService, model) -> int:
    async with service.transaction():
        result = await service.session.execute(select(func.count()).select_from(model))
        return int(result.scalar_one())


@pytest.mark.parametrize(
    "model, expected_count",
    [
        (UserORM, 4),
        (WalletORM, 4),
        (MLModelORM, 4),
        (MLTaskORM, 5),
        (PredictionResultORM, 2),
        (TransactionORM, 6),
    ],
    ids=lambda x: x.__tablename__ if hasattr(x, "__tablename__") else str(x),
)
async def test_row_counts(service: DatabaseService, model, expected_count: int) -> None:
    actual = await _count(service, model)
    assert actual == expected_count, (
        f"{model.__tablename__}: expected {expected_count} rows, got {actual}"
    )


async def test_admin_exists(service: DatabaseService) -> None:
    async with service.transaction():
        admin = (
            await service.session.execute(select(UserORM).where(UserORM.username == "admin"))
        ).scalar_one_or_none()

        assert admin is not None, "admin user not found"
        assert admin.email == "admin@example.com", f"bad admin email: {admin.email!r}"
        assert admin.role == UserRoleORM.ADMIN, f"bad admin role: {admin.role!r}"


async def test_every_user_has_wallet(service: DatabaseService) -> None:
    async with service.transaction():
        users = (await service.session.execute(select(UserORM))).scalars().all()
        wallets_by_user = {
            w.user_id: w
            for w in (await service.session.execute(select(WalletORM))).scalars().all()
        }
        for user in users:
            assert user.id in wallets_by_user, (
                f"user {user.username!r} (id={user.id}) has no wallet"
            )


async def test_completed_tasks_have_results(service: DatabaseService) -> None:
    async with service.transaction():
        completed = (
            await service.session.execute(
                select(MLTaskORM).where(MLTaskORM.status == TaskStatusORM.COMPLETED)
            )
        ).scalars().all()

        result_task_ids = {
            r.task_id
            for r in (await service.session.execute(select(PredictionResultORM))).scalars().all()
        }

        for task in completed:
            assert task.id in result_task_ids, (
                f"completed task id={task.id} has no PredictionResult"
            )


async def test_debit_transactions_reference_tasks(service: DatabaseService) -> None:
    async with service.transaction():
        debits = (
            await service.session.execute(
                select(TransactionORM).where(
                    TransactionORM.transaction_type == TransactionTypeORM.DEBIT
                )
            )
        ).scalars().all()

        assert len(debits) > 0, "expected at least one DEBIT transaction"

        for tx in debits:
            assert tx.ml_task_id is not None, (
                f"DEBIT transaction id={tx.id} has no ml_task_id"
            )
