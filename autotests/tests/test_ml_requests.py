"""
  - submit task - 202
  - get task by id (owner only)
  - another user cannot access someone else's task - 403
  - invalid model id - 404 (no task, no deduction)
  - inactive model - 422 (no task, no deduction)
  - non-dict input_data - 422 (no task, no deduction)
  - insufficient balance - task FAILED, balance unchanged
  - end-to-end: task COMPLETED, balance decremented, result present  [slow]

Fixtures:
  model id=1  sentiment-analyzer  cost=1.0  is_active=True
  model id=4  deprecated-model    cost=5.0  is_active=False
  charlie wallet = 0.0
"""
import pytest

from conftest import UserClient

ACTIVE_MODEL_ID = 1
INACTIVE_MODEL_ID = 4
ACTIVE_MODEL_COST = 1.0
VALID_INPUT = {"text": "I love this product!"}


class TestSubmitTask:
    def test_submit_task_returns_202(self, alice: UserClient) -> None:
        resp = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT)
        assert resp.status_code == 202

    def test_submit_task_response_has_expected_fields(self, alice: UserClient) -> None:
        body = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()
        assert "id" in body
        assert body["status"] in ("pending", "processing", "completed", "failed")
        assert body["model_id"] == ACTIVE_MODEL_ID

    def test_owner_can_get_own_task(self, alice: UserClient) -> None:
        task_id = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        resp = alice.get_task(task_id)
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_anon_cannot_submit_task(self, anon: UserClient) -> None:
        assert anon.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).status_code == 401

    def test_get_nonexistent_task_returns_404(self, alice: UserClient) -> None:
        assert alice.get_task(999999).status_code == 404


class TestCrossUserIsolation:
    def test_bob_cannot_access_alices_task(self, alice: UserClient, bob: UserClient) -> None:
        task_id = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        assert bob.get_task(task_id).status_code == 403

    def test_alice_cannot_access_bobs_task(self, alice: UserClient, bob: UserClient) -> None:
        task_id = bob.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        assert alice.get_task(task_id).status_code == 403

    def test_fresh_user_cannot_access_alices_task(
        self, alice: UserClient, fresh_user: UserClient
    ) -> None:
        task_id = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        assert fresh_user.get_task(task_id).status_code == 403

    def test_anon_cannot_access_any_task(self, alice: UserClient, anon: UserClient) -> None:
        task_id = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        assert anon.get_task(task_id).status_code == 401

    def test_task_list_is_per_user(self, alice: UserClient, fresh_user: UserClient) -> None:
        """A fresh user's task list must not contain Alice's tasks."""
        alice_task_id = alice.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        fresh_tasks = fresh_user.list_tasks().json()
        fresh_task_ids = {t["id"] for t in fresh_tasks}
        assert alice_task_id not in fresh_task_ids


class TestInvalidTaskRequests:
    def test_invalid_model_id_returns_404(self, alice: UserClient) -> None:
        assert alice.submit_task(999999, VALID_INPUT).status_code == 404

    def test_inactive_model_returns_422(self, alice: UserClient) -> None:
        assert alice.submit_task(INACTIVE_MODEL_ID, VALID_INPUT).status_code == 422

    def test_non_dict_input_returns_422(self, alice: UserClient) -> None:
        assert alice.submit_task(ACTIVE_MODEL_ID, "plain string").status_code == 422

    def test_list_input_returns_422(self, alice: UserClient) -> None:
        assert alice.submit_task(ACTIVE_MODEL_ID, [1, 2, 3]).status_code == 422


class TestCreditDeduction:
    def test_no_deduction_on_invalid_model(self, fresh_user: UserClient) -> None:
        """Request rejected before billing — balance must not change."""
        fresh_user.deposit(100.0)
        balance_before = fresh_user.get_balance().json()["amount"]
        fresh_user.submit_task(999999, VALID_INPUT)
        assert fresh_user.get_balance().json()["amount"] == balance_before

    def test_no_deduction_on_invalid_input_data(self, fresh_user: UserClient) -> None:
        """Non-dict input is rejected before billing — balance must not change."""
        fresh_user.deposit(100.0)
        balance_before = fresh_user.get_balance().json()["amount"]
        fresh_user.submit_task(ACTIVE_MODEL_ID, "not a dict")
        assert fresh_user.get_balance().json()["amount"] == balance_before

    def test_no_deduction_on_inactive_model(self, fresh_user: UserClient) -> None:
        fresh_user.deposit(100.0)
        balance_before = fresh_user.get_balance().json()["amount"]
        fresh_user.submit_task(INACTIVE_MODEL_ID, VALID_INPUT)
        assert fresh_user.get_balance().json()["amount"] == balance_before

    def test_insufficient_funds_task_eventually_fails(self, charlie: UserClient) -> None:
        """Charlie has 0.0 balance — billing fails - task status must become FAILED."""
        task_id = charlie.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        task = charlie.poll_task(task_id, timeout=30)
        assert task["status"] == "failed"

    def test_insufficient_funds_balance_unchanged(self, charlie: UserClient) -> None:
        """Charlie's balance must stay at 0.0 after a billing-failed task."""
        balance_before = charlie.get_balance().json()["amount"]
        task_id = charlie.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        charlie.poll_task(task_id, timeout=30)
        assert charlie.get_balance().json()["amount"] == balance_before

    def test_charlies_failed_task_not_visible_to_alice(
        self, alice: UserClient, charlie: UserClient
    ) -> None:
        task_id = charlie.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        assert alice.get_task(task_id).status_code == 403


@pytest.mark.slow
class TestEndToEndMLFlow:
    """Full async flow: submit - billing - worker - result. Requires worker with cached models."""

    def test_task_completes_with_result(self, fresh_user: UserClient) -> None:
        fresh_user.deposit(50.0)
        task_id = fresh_user.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        task = fresh_user.poll_task(task_id, timeout=120)
        assert task["status"] == "completed"
        assert task["result"] is not None
        assert "output_data" in task["result"]
        assert task["result"]["credits_charged"] == ACTIVE_MODEL_COST

    def test_balance_decremented_after_completed_task(self, fresh_user: UserClient) -> None:
        fresh_user.deposit(50.0)
        balance_before = fresh_user.get_balance().json()["amount"]
        task_id = fresh_user.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        fresh_user.poll_task(task_id, timeout=120)
        balance_after = fresh_user.get_balance().json()["amount"]
        assert balance_after == balance_before - ACTIVE_MODEL_COST

    def test_completed_task_not_visible_to_other_user(
        self, fresh_user: UserClient, bob: UserClient
    ) -> None:
        fresh_user.deposit(50.0)
        task_id = fresh_user.submit_task(ACTIVE_MODEL_ID, VALID_INPUT).json()["id"]
        fresh_user.poll_task(task_id, timeout=120)
        assert bob.get_task(task_id).status_code == 403
