"""Worker handler behavior with mocked repositories.

These tests patch the repository classes imported by the worker module so
no real database is needed. They cover the three branches that matter:
happy path, predict-fails-refund, and task-not-found-skip.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ml_service.messaging import worker as worker_module
from ml_service.messaging.schemas import PredictTaskMessage


class _FakeDB:
    @asynccontextmanager
    async def transaction(self):
        yield


def _make_msg() -> PredictTaskMessage:
    return PredictTaskMessage(
        task_id=7,
        user_id=1,
        model_id=2,
        submitted_at=datetime.now(timezone.utc),
    )


def _make_task(status_value: str = "pending"):
    task = MagicMock()
    task.task_id = 7
    task.user.user_id = 1
    task.model.name = "mock-model"
    task.model.cost_per_request = 5.0
    task.input_data = {"a": 1}
    task.status.value = status_value
    # Make `task.status != TaskStatus.PENDING` only when we want it to.
    from ml_service_model.domains.task import TaskStatus

    task.status = TaskStatus(status_value)
    return task


@pytest.fixture
def mock_repos():
    """Patch every repository class the worker imports to a fresh AsyncMock."""
    with (
        patch.object(worker_module, "SqlAlchemyAltMLTaskRepository") as task_cls,
        patch.object(worker_module, "SqlAlchemyAltPredictionResultRepository") as result_cls,
        patch.object(worker_module, "SqlAlchemyAltUserRepository") as user_cls,
        patch.object(worker_module, "SqlAlchemyAltBalanceRepository") as balance_cls,
        patch.object(worker_module, "SqlAlchemyAltTransactionRepository") as tx_cls,
    ):
        repos = {
            "task": AsyncMock(),
            "result": AsyncMock(),
            "user": AsyncMock(),
            "balance": AsyncMock(),
            "tx": AsyncMock(),
        }
        task_cls.return_value = repos["task"]
        result_cls.return_value = repos["result"]
        user_cls.return_value = repos["user"]
        balance_cls.return_value = repos["balance"]
        tx_cls.return_value = repos["tx"]
        yield repos


class TestHappyPath:
    async def test_marks_processing_then_completed_and_saves_result(self, mock_repos) -> None:
        task = _make_task("pending")
        mock_repos["task"].get_by_id.return_value = task

        predictor = MagicMock()
        predictor.predict.return_value = {"score": 0.5}

        handler = worker_module.TaskHandler(_FakeDB(), predictor)
        ok = await handler.handle(_make_msg())

        assert ok is True
        predictor.predict.assert_called_once_with("mock-model", {"a": 1})
        # task was updated twice: PROCESSING then COMPLETED.
        assert mock_repos["task"].update.call_count == 2
        # PredictionResult was saved exactly once.
        mock_repos["result"].save.assert_called_once()


class TestPredictFails:
    async def test_marks_failed_and_refunds(self, mock_repos) -> None:
        from ml_service_users.domains.user import User
        from ml_service_wallet.domains.wallet import Wallet

        task = _make_task("pending")
        mock_repos["task"].get_by_id.return_value = task

        user = User(user_id=1, username="u", email="u@example.com", password_hash="x")
        wallet = Wallet(user_id=1, amount=10.0)
        mock_repos["user"].get_by_id.return_value = user
        mock_repos["balance"].get_by_user_id.return_value = wallet
        mock_repos["tx"].save.side_effect = lambda tx: tx

        predictor = MagicMock()
        predictor.predict.side_effect = RuntimeError("model exploded")

        handler = worker_module.TaskHandler(_FakeDB(), predictor)
        ok = await handler.handle(_make_msg())

        assert ok is False
        # refund was applied to the wallet
        assert wallet.amount == 15.0
        # the saved transaction is a deposit linked to the task
        saved = mock_repos["tx"].save.call_args[0][0]
        assert saved.transaction_type.value == "deposit"
        assert saved.ml_task_id == 7
        # task got at least one update beyond PROCESSING (FAILED)
        assert mock_repos["task"].update.call_count >= 2


class TestTaskMissing:
    async def test_skips_when_db_has_no_task(self, mock_repos) -> None:
        mock_repos["task"].get_by_id.return_value = None

        handler = worker_module.TaskHandler(_FakeDB(), MagicMock())
        ok = await handler.handle(_make_msg())

        assert ok is False
        mock_repos["task"].update.assert_not_called()


class TestUserMismatch:
    async def test_rejects_message_pointing_at_other_user(self, mock_repos) -> None:
        task = _make_task("pending")
        task.user.user_id = 999  # not 1
        from ml_service_model.domains.task import TaskStatus

        # Re-set since _make_task overwrote .status
        task.status = TaskStatus.PENDING
        mock_repos["task"].get_by_id.return_value = task

        handler = worker_module.TaskHandler(_FakeDB(), MagicMock())
        ok = await handler.handle(_make_msg())

        assert ok is False
        mock_repos["task"].update.assert_not_called()
